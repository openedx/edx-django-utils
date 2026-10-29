"""
Tests for util.logging
"""

import re
import subprocess

import pytest

from edx_django_utils.logging.internal.log_sensitive import decrypt_log_message, encrypt_for_log, generate_reader_keys


def test_encryption_no_key():
    to_log = encrypt_for_log("Testing testing 1234", None)
    assert to_log == '[encryption failed, no key]'


def test_encryption_round_trip():
    reader_keys = generate_reader_keys()
    reader_public_64 = reader_keys['public']
    reader_private_64 = reader_keys['private']

    to_log = encrypt_for_log("Testing testing 1234", reader_public_64)
    re_base64 = r'[a-zA-Z0-9/+=]'
    assert re.fullmatch(f'\\[encrypted: {re_base64}+\\|{re_base64}+\\]', to_log)

    to_decrypt = to_log.partition('[encrypted: ')[2].rstrip(']')

    decrypted = decrypt_log_message(to_decrypt, reader_private_64)
    assert decrypted == "Testing testing 1234"

    # Also check that decryption still works if someone accidentally
    # copies in the trailing framing "]" character, just as a
    # nice-to-have. (base64 module should handle this already, since
    # it stops reading at the first invalid base64 character.)
    decrypted_again = decrypt_log_message(to_decrypt + ']', reader_private_64)
    assert decrypted_again == "Testing testing 1234"


def test_full_cli(tmp_path):
    def do_call(args, stdin=None):
        return subprocess.run(
            ['log-sensitive', *args], check=True,
            input=(stdin.encode() if stdin else None), capture_output=True,
        ).stdout.decode()

    # Generate keys and save the private key to file
    genkeys_out = do_call(['gen-keys'])
    gen_pub_64 = re.search(r'YOUR_DEBUG_PUBLIC_KEY[^"]*"([^"]*)"', genkeys_out).group(1)
    gen_priv_64 = re.search(r'"([^"]*)" \(private\)', genkeys_out).group(1)
    priv_key_file = tmp_path / 'log_sensitive_private.key'
    with open(priv_key_file, 'w') as priv_f:
        priv_f.write(gen_priv_64)

    sample_plaintext = "The Magic Words are Squeamish Ossifrage"

    encrypted_raw = do_call(
        ['encrypt', '--public-key', gen_pub_64, '--message-file', '-'],
        stdin=sample_plaintext
    )

    # Check that there's a useful error message if the [encrypted: ...] wrapper is left in
    with pytest.raises(subprocess.CalledProcessError) as e:
        decrypted = do_call(
            ['decrypt', '--private-key-file', priv_key_file, '--message-file', '-'],
            stdin=encrypted_raw
        )
    assert 'Only include the Base64' in e.value.stderr.decode()

    # Get rid of [encrypted: ...] wrapper/delimiter
    encrypted = encrypted_raw.split(' ')[1].rstrip(']')
    decrypted = do_call(
        ['decrypt', '--private-key-file', priv_key_file, '--message-file', '-'],
        stdin=encrypted
    )

    # Decrypted output comes out of CLI with an extra \n, so get rid of that first
    assert decrypted.strip('\n') == sample_plaintext

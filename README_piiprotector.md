# PII Protector

A Python script that removes Personally Identifiable Information (PII) from text by masking out user-defined words. It's designed to work in a pipe, making it easy to integrate with other command-line tools.

## Installation

1. Make the script executable:
   ```bash
   chmod +x piiprotector
   ```

2. (Optional) Move it to a directory in your PATH:
   ```bash
   sudo mv piiprotector /usr/local/bin/
   ```

## Usage

Basic usage in a pipe:
```bash
cat input.txt | piiprotector | pbcopy
```

Or with echo:
```bash
echo "Your text with PII" | piiprotector
```

### Command Line Options

- `--config` or `-c`: Specify the path to the PII words configuration file (default: `~/.piiprotector_words.txt`)
- `--mask` or `-m`: Specify the character to use for masking (default: `*`)

Examples:
```bash
# Use a custom config file
cat sensitive.txt | piiprotector --config /path/to/custom_words.txt

# Use a different mask character
cat sensitive.txt | piiprotector --mask "#"
```

## Configuration

The script uses a configuration file to define which words or phrases should be masked. By default, it looks for `~/.piiprotector_words.txt`.

### Creating a Configuration File

1. Create a file with one word or phrase per line
2. Lines starting with `#` are treated as comments and ignored
3. The matching is case-insensitive

Example configuration file:
```
# Personal Information
John Doe
Jane Smith
john.doe@example.com

# Project Names
Project Alpha
SecretProject

# Company Information
Acme Corporation
```

## How It Works

1. The script reads text from standard input
2. It loads the list of PII words from the configuration file
3. It replaces each occurrence of the PII words with mask characters (same length as the original word)
4. It outputs the filtered text to standard output

## Examples

### Basic Example
```bash
$ echo "Contact John Doe from Acme Corporation about Project Alpha" | ./piiprotector --config piiprotector_words.txt
Contact ******** from **************** about *************
```

### With pbcopy (macOS)
```bash
$ cat sensitive_document.txt | ./piiprotector | pbcopy
# The filtered text is now in your clipboard
```

### With Different Mask Character
```bash
$ echo "Contact John Doe" | ./piiprotector --config piiprotector_words.txt --mask "#"
Contact ########
```

## Tips

1. Keep your configuration file in a secure location as it contains sensitive information
2. Regularly update your configuration file with new PII words as needed
3. The script works best with exact matches - consider adding variations of the same word if needed
4. For email addresses, add both the full email and just the username part if needed

## Troubleshooting

- If no words are being masked, check that your configuration file exists and is properly formatted
- The script will display a warning if it can't find the configuration file
- Make sure the script is executable if you're getting permission errors

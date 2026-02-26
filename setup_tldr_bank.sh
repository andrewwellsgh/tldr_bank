#!/usr/bin/env bash

echo "Installing Tl;Dr Bank..."

# Ensure poetry exists
if ! command -v poetry &> /dev/null
then
    echo "Poetry not found. Installing..."
    curl -sSL https://install.python-poetry.org | python3 -
fi

# Install dependencies
poetry install

# Add CLI entry
echo "Creating CLI entry..."

mkdir -p ~/.local/bin

cat <<EOF > ~/.local/bin/tldr_bank
#!/usr/bin/env bash
cd "$(pwd)"
poetry run python -m tldr_bank.main "\$@"
EOF

chmod +x ~/.local/bin/tldr_bank

echo ""
echo "Installation complete!"
echo "Run with:"
echo ""
echo "    tldr_bank"
echo ""
echo "Or show all:"
echo ""
echo "    tldr_bank --all"
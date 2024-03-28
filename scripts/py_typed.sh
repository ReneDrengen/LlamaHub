#!/bin/bash

# Usage: ./py-typed.sh [check|create]

MODE="$1" # The operation mode: "check" or "create"
MISSING_PY_TYPED=0 # Flag to track missing py.typed files

increment_patch_version() {
    local version=$1
    IFS='.' read -ra PARTS <<< "$version" # Split version into an array.
    local major=${PARTS[0]}
    local minor=${PARTS[1]}
    local patch=${PARTS[2]}
    ((patch++)) # Increment patch
    echo "${major}.${minor}.${patch}" # Return new version
}

# This function processes directories based on the mode.
process_directory() {
    local dir=$1
    local found_py_files=false

    # Check for Python files in the current directory.
    if ls "$dir"/*.py &>/dev/null; then
        found_py_files=true
        if [[ $MODE == "create" && ! -f "$dir/py.typed" ]]; then
            echo "Creating py.typed in $dir"
            touch "$dir/py.typed"
        elif [[ $MODE == "check" ]]; then
            if [[ ! -f "$dir/py.typed" ]]; then
                echo "ERROR: Missing py.typed in $dir"
                MISSING_PY_TYPED=1 # Mark as missing
            fi
        fi
    fi

    # Stop recursion if Python files were found.
    if $found_py_files; then
        return
    fi

    # Recursively process subdirectories.
    for subdir in "$dir"/*/; do
        if [[ -d $subdir ]]; then
            process_directory "$subdir"
        fi
    done
}

# Validate mode.
if [[ $MODE != "check" && $MODE != "create" ]]; then
    echo "Error: You must specify either 'check' or 'create' mode."
    echo "Usage: $0 [check|create]"
    exit 1
fi

# Main execution starts here.
find . -type f -name "pyproject.toml" | while read -r toml_file; do
    base_dir=$(dirname "$toml_file")
    llama_index_dir="$base_dir/llama_index"

    if [ -d "$llama_index_dir" ]; then
        process_directory "$llama_index_dir"
        if [[ $MODE == "create" ]]; then
            current_version=$(grep '^version =' "$toml_file" | head -1 | sed 's/version = "\(.*\)"/\1/')
            if [[ ! -z "$current_version" ]]; then
                new_version=$(increment_patch_version "$current_version")
                sed -i "s/version = \"$current_version\"/version = \"$new_version\"/" "$toml_file"
                echo "Updated $toml_file to version $new_version."
            else
                echo "No version found in $toml_file."
            fi
        fi
    fi
done

# If in check mode and any py.typed files are missing, exit with code 1.
if [[ $MODE == "check" && $MISSING_PY_TYPED -eq 1 ]]; then
    echo "One or more py.typed files are missing."
    exit 1
else
    echo "All necessary py.typed files present."
fi

# Final message for create mode to indicate process completion
if [[ $MODE == "create" ]]; then
    echo "py.typed creation and version increment completed."
fi

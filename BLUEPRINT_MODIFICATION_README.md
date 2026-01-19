# Blueprint Modification Guide

This project uses [dspbptk](https://github.com/johndoe31415/dspbptk) to modify Dyson Sphere Program blueprint files programmatically.

## Setup

The `dspbptk` toolkit has been cloned into the `dspbptk/` directory. The modification script `modify_blueprint.py` is ready to use.

## Requirements

- Python 3.6 or higher
- The dspbptk toolkit (already included in this repository)

## Usage

### Basic Commands

#### 1. Dump Blueprint Information

View information about a blueprint:

```bash
python3 modify_blueprint.py dump <blueprint_file>
```

Example:
```bash
python3 modify_blueprint.py dump "Power-GenerationOther_Other-Power/[A-demon.]StarChargingstake/Medium-LatitudeEnergy-ExchangerChargingDevice.txt"
```

#### 2. Convert Blueprint to JSON

Convert a blueprint to JSON format for easier inspection and modification:

```bash
python3 modify_blueprint.py to-json <input_blueprint> <output_json> [--pretty]
```

Example:
```bash
python3 modify_blueprint.py to-json "blueprint.txt" "blueprint.json" --pretty
```

#### 3. Convert JSON back to Blueprint

Convert a modified JSON file back to blueprint format:

```bash
python3 modify_blueprint.py from-json <input_json> <output_blueprint>
```

Example:
```bash
python3 modify_blueprint.py from-json "modified_blueprint.json" "new_blueprint.txt"
```

#### 4. Modify Blueprint

Modify a blueprint file directly:

```bash
python3 modify_blueprint.py modify <input_blueprint> <output_blueprint> [options]
```

Options:
- `--short-desc "Description"` - Set the short description
- `--long-desc "Description"` - Set the long description
- `--modifications <json_file>` - Apply modifications from a JSON file
- `--ignore-corrupt` - Skip hash validation (use with caution)

Example:
```bash
python3 modify_blueprint.py modify "input.txt" "output.txt" --short-desc "My Modified Blueprint"
```

## Workflow: Modifying Blueprint Data

To modify the actual blueprint data (buildings, positions, settings, etc.):

1. **Convert to JSON:**
   ```bash
   python3 modify_blueprint.py to-json "original.txt" "original.json" --pretty
   ```

2. **Edit the JSON file** using any text editor or script. The JSON contains:
   - Building positions and rotations
   - Item IDs (for upgrading belts, sorters, etc.)
   - Logistics station settings
   - Recipe assignments
   - And more...

3. **Convert back to blueprint:**
   ```bash
   python3 modify_blueprint.py from-json "modified.json" "modified.txt"
   ```

## Example: Upgrading Belts

To upgrade all Mk1 belts to Mk2 in a blueprint:

1. Convert to JSON:
   ```bash
   python3 modify_blueprint.py to-json "factory.txt" "factory.json" --pretty
   ```

2. Use a script to modify the JSON (or edit manually):
   ```python
   import json
   
   with open('factory.json', 'r') as f:
       data = json.load(f)
   
   # Find all ConveyorBeltMKI and change to ConveyorBeltMKII
   for area in data.get('areas', []):
       for building in area.get('buildings', []):
           if building.get('item_id') == 'ConveyorBeltMKI':
               building['item_id'] = 'ConveyorBeltMKII'
   
   with open('factory_modified.json', 'w') as f:
       json.dump(data, f, indent=2)
   ```

3. Convert back:
   ```bash
   python3 modify_blueprint.py from-json "factory_modified.json" "factory_upgraded.txt"
   ```

## Using dspbptk Directly

You can also use dspbptk directly:

```bash
cd dspbptk
python3 dspbptk dump "path/to/blueprint.txt"
python3 dspbptk bp2json "path/to/blueprint.txt" "output.json" --pretty-print
python3 dspbptk json2bp "input.json" "output.txt"
python3 dspbptk edit --short-desc "New description" "input.txt" "output.txt"
```

## Important Notes

1. **Always backup your blueprints** before modifying them
2. **Hash validation**: Blueprints have a hash that validates their integrity. The toolkit automatically recalculates this hash when saving
3. **Game version**: Blueprints are tied to specific game versions. Modifying blueprints from newer versions may not work in older versions
4. **Testing**: Always test modified blueprints in-game before using them in important saves

## Troubleshooting

### "Invalid hash value" error
- Use `--ignore-corrupt` flag if you're sure the blueprint is valid but hash check fails
- This might indicate the blueprint format has changed

### Import errors
- Make sure you're running the script from the Blueprint directory
- Ensure Python 3.6+ is installed

### Blueprint doesn't load in game
- Check that the game version matches
- Verify the JSON structure is correct if you modified it manually
- Try converting back and forth without modifications first

## Advanced Usage

For more advanced modifications, you can:

1. **Use the Blueprint class directly** in Python:
   ```python
   from Blueprint import Blueprint
   
   bp = Blueprint.read_from_file("blueprint.txt")
   bp.short_desc = "New description"
   bp_data = bp.decoded_data
   # Modify bp_data as needed
   bp.write_to_file("output.txt")
   ```

2. **Extend the modify_blueprint.py script** with custom modification functions

3. **Use the JSON format** for complex batch modifications

## References

- [dspbptk GitHub Repository](https://github.com/johndoe31415/dspbptk)
- [Dyson Sphere Program Wiki](https://dsp-wiki.com/)

## License

This script uses dspbptk, which is licensed under GPL-3.0.

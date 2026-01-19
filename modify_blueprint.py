#!/usr/bin/env python3
"""
Blueprint modification script using dspbptk.

This script allows you to modify Dyson Sphere Program blueprints programmatically.
It uses the dspbptk library to decode, modify, and re-encode blueprints.
"""

import sys
import os
import json
import argparse
from pathlib import Path

# Add dspbptk to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'dspbptk'))

from Blueprint import Blueprint
from BlueprintData import BlueprintData


def modify_blueprint_data(bp_data, modifications):
    """
    Modify blueprint data based on a dictionary of modifications.
    
    Args:
        bp_data: BlueprintData object from dspbptk
        modifications: Dictionary with modification instructions
        
    Returns:
        Modified BlueprintData object
    """
    # Example modifications you can do:
    # - Change building positions
    # - Change item IDs (upgrade belts, sorters, etc.)
    # - Modify logistics station settings
    # - Change recipes
    
    if 'buildings' in modifications:
        # Modify buildings
        for building_mod in modifications['buildings']:
            # Example: upgrade all Mk1 belts to Mk2
            # This would require iterating through buildings and changing item_id
            pass
    
    if 'logistics_stations' in modifications:
        # Modify logistics station settings
        for station_mod in modifications['logistics_stations']:
            # Example: change storage settings, drone counts, etc.
            pass
    
    return bp_data


def modify_blueprint_file(input_file, output_file, modifications=None, 
                          short_desc=None, long_desc=None, ignore_corrupt=False):
    """
    Read a blueprint file, modify it, and write it back.
    
    Args:
        input_file: Path to input blueprint file
        output_file: Path to output blueprint file
        modifications: Dictionary of data modifications (optional)
        short_desc: New short description (optional)
        long_desc: New long description (optional)
        ignore_corrupt: Skip hash validation (optional)
    """
    # Read the blueprint
    print(f"Reading blueprint from: {input_file}")
    bp = Blueprint.read_from_file(input_file, validate_hash=not ignore_corrupt)
    
    # Modify metadata
    if short_desc is not None:
        print(f"Setting short description to: {short_desc}")
        bp.short_desc = short_desc
    
    if long_desc is not None:
        print(f"Setting long description to: {long_desc}")
        bp.long_desc = long_desc
    
    # Modify blueprint data if modifications provided
    if modifications:
        print("Applying data modifications...")
        bp_data = bp.decoded_data
        modified_data = modify_blueprint_data(bp_data, modifications)
        # Note: You'll need to set the modified data back to the blueprint
        # This might require accessing internal _data property
    
    # Write the modified blueprint
    print(f"Writing modified blueprint to: {output_file}")
    bp.write_to_file(output_file)
    print("Done!")


def convert_to_json(input_file, output_file, pretty_print=False, ignore_corrupt=False):
    """
    Convert a blueprint file to JSON format for easier inspection/modification.
    
    Args:
        input_file: Path to input blueprint file
        output_file: Path to output JSON file
        pretty_print: Whether to pretty-print the JSON
        ignore_corrupt: Skip hash validation
    """
    print(f"Converting blueprint to JSON: {input_file} -> {output_file}")
    
    # Use dspbptk's built-in JSON conversion via command-line interface
    from ActionBlueprintToJSON import ActionBlueprintToJSON
    
    args = argparse.Namespace(
        infile=input_file,
        outfile=output_file,
        force=True,
        pretty_print=pretty_print,
        ignore_corrupt=ignore_corrupt,
        verbose=0
    )
    
    # Create action instance properly
    class ActionWrapper(ActionBlueprintToJSON):
        def __init__(self, args):
            self._cmd = 'bp2json'
            self._args = args
            self.run()
    
    ActionWrapper(args)
    print("Done!")


def convert_from_json(input_file, output_file, ignore_corrupt=False):
    """
    Convert a JSON file back to blueprint format.
    
    Args:
        input_file: Path to input JSON file
        output_file: Path to output blueprint file
        ignore_corrupt: Skip validation
    """
    print(f"Converting JSON to blueprint: {input_file} -> {output_file}")
    from ActionJSONToBlueprint import ActionJSONToBlueprint
    
    args = argparse.Namespace(
        infile=input_file,
        outfile=output_file,
        force=True,
        ignore_corrupt=ignore_corrupt,
        verbose=0
    )
    
    class ActionWrapper(ActionJSONToBlueprint):
        def __init__(self, args):
            self._cmd = 'json2bp'
            self._args = args
            self.run()
    
    ActionWrapper(args)
    print("Done!")


def dump_blueprint_info(input_file, ignore_corrupt=False):
    """
    Dump information about a blueprint.
    
    Args:
        input_file: Path to blueprint file
        ignore_corrupt: Skip hash validation
    """
    from ActionDump import ActionDump
    import collections
    from Enums import DysonSphereItem
    
    bp = Blueprint.read_from_file(input_file, validate_hash=not ignore_corrupt)
    bpd = bp.decoded_data
    
    building_counter = collections.Counter()
    for building in bpd.buildings:
        building_counter[building.data.item_id] += 1
    
    if bp.short_desc != "":
        print("Text          : %s" % (bp.short_desc))
    if bp.long_desc != "":
        print("Description   : %s" % (bp.long_desc))
    print("Game version  : %s" % (bp.game_version))
    print("Building count: %d" % (len(bpd.buildings)))
    for (item_id, count) in building_counter.most_common():
        try:
            item = DysonSphereItem(item_id)
            item_name = item.name
        except ValueError:
            item_name = f"[{item_id}]"
        print("%5d  %s" % (count, item_name))


def main():
    parser = argparse.ArgumentParser(
        description="Modify Dyson Sphere Program blueprints using dspbptk"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Modify command
    modify_parser = subparsers.add_parser('modify', help='Modify a blueprint file')
    modify_parser.add_argument('input', help='Input blueprint file')
    modify_parser.add_argument('output', help='Output blueprint file')
    modify_parser.add_argument('--short-desc', help='Set short description')
    modify_parser.add_argument('--long-desc', help='Set long description')
    modify_parser.add_argument('--modifications', help='JSON file with modifications')
    modify_parser.add_argument('--ignore-corrupt', action='store_true', 
                              help='Skip hash validation')
    
    # Convert to JSON command
    json_parser = subparsers.add_parser('to-json', help='Convert blueprint to JSON')
    json_parser.add_argument('input', help='Input blueprint file')
    json_parser.add_argument('output', help='Output JSON file')
    json_parser.add_argument('--pretty', action='store_true', 
                            help='Pretty-print JSON')
    json_parser.add_argument('--ignore-corrupt', action='store_true',
                            help='Skip hash validation')
    
    # Convert from JSON command
    bp_parser = subparsers.add_parser('from-json', help='Convert JSON to blueprint')
    bp_parser.add_argument('input', help='Input JSON file')
    bp_parser.add_argument('output', help='Output blueprint file')
    bp_parser.add_argument('--ignore-corrupt', action='store_true',
                          help='Skip hash validation')
    
    # Dump command
    dump_parser = subparsers.add_parser('dump', help='Dump blueprint information')
    dump_parser.add_argument('input', help='Input blueprint file')
    dump_parser.add_argument('--ignore-corrupt', action='store_true',
                            help='Skip hash validation')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        if args.command == 'modify':
            modifications = None
            if args.modifications:
                with open(args.modifications, 'r') as f:
                    modifications = json.load(f)
            
            modify_blueprint_file(
                args.input,
                args.output,
                modifications=modifications,
                short_desc=args.short_desc,
                long_desc=args.long_desc,
                ignore_corrupt=args.ignore_corrupt
            )
        
        elif args.command == 'to-json':
            convert_to_json(
                args.input,
                args.output,
                pretty_print=args.pretty,
                ignore_corrupt=args.ignore_corrupt
            )
        
        elif args.command == 'from-json':
            convert_from_json(
                args.input,
                args.output,
                ignore_corrupt=args.ignore_corrupt
            )
        
        elif args.command == 'dump':
            dump_blueprint_info(
                args.input,
                ignore_corrupt=args.ignore_corrupt
            )
        
        return 0
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())

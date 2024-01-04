# Unpacker Utility
Helper tool for [Bundle Unpacker](https://gitlab.com/lschwiderski/vt2_bundle_unpacker/) to extract files or batch decompile lua scripts using [LuaJIT Decompiler v2](https://github.com/Aussiemon/luajit-decompiler-v2)

# Instllation
1. Download the latest zip package from [Releases](https://github.com/thewhitegoatcb/Unpacker_Util/releases).
2. Extract it in your prefered location.
3. Follow the Usage guide below or use the `extract_decompile_lua.bat` or `extract_strings.bat` scripts
## Usage
    python .\unpacker_util.py <bundles_path> [global_options] <unpack/decompile> [command_options] [command_arguments]

### Global Options
|Flag|Value|Default|Description|
|----|-----|-------|-----------|
|`bundles_path`|Bundles Path||__Required__ positional argument with the path to where the bundles are contained with the `bundle_database.data` file|
|`--output_path`, `-o`|Output Path|`./output`|Path of where to put the extracted/decompiled files|
|`--unpacker_path`, `-u`|Unpacker Path|`./unpacker.exe`|Path of the unpacker exe file|
|`--clear`,`-c`|Flag|`False`|Remove the output directory before any operation|
|`--verbose`,`-v`|Flag|`False`|Prints debug information|


### Unpack
|Flag|Value|Default|Description|
|----|-----|-------|-----------|
|`--flatten`,`-f`|Flag|`False`|Doesn't create internal bundle folders, just unpack into the output folder|
|`--pass_args`,`-p`|Arguments||Arguments to pass to the unpacker, see [Unpacker Extract CLI](https://gitlab.com/lschwiderski/vt2_bundle_unpacker/-/wikis/cli_reference#user-content-extract)

#### Example
From `extract_strings.bat`:

    python .\unpacker_util.py "C:\Program Files (x86)\Steam\steamapps\common\Warhammer Vermintide 2\bundle" --clear --output_path ".\game_strings" unpack --pass_args "-d -i *.strings"

### Decompile
|Flag|Value|Default|Description|
|----|-----|-------|-----------|
|`--decompiler_path`,`-d`|Decompiler Path|`./luajit-decompiler-v2.exe`|Path to the decompiler exe|
#### Example
From `extract_decompile_lua.bat`:

    python .\unpacker_util.py "C:\Program Files (x86)\Steam\steamapps\common\Warhammer Vermintide 2\bundle" --clear --output_path ".\game_source" decompile


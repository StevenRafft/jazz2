# data
assets_run = """for %%i in (./assets/*.*) do (
  copy ".\\assets\\%%i" "%GAME_DIRECTORY%\\$N$_%%i" /y
)"""

angelscriptpp_run = """for %%i in (*.j2as *.mut *.asc) do (
  python ../../experiments/angelscriptpp/angelscriptpp.py "%%i" "%GAME_DIRECTORY%\\%%i" -P "$N$"
)"""

angelscriptpp_copy = """for %%i in (*.j2l *.j2t) do (
  copy "%%i" "%GAME_DIRECTORY%" /y
)"""

normal_copy = """for %%i in (*.j2l *.j2as *.mut *.asc *.j2t) do (
  copy "%%i" "%GAME_DIRECTORY%" /y
)"""

run = """@echo off

REM Read variables from run.ini
for /f "tokens=1* delims==" %%a in ('type "..\\..\\run.ini" ^| find "="') do (
  if /i "%%a"=="GAME_DIRECTORY" set "GAME_DIRECTORY=%%b"
  if /i "%%a"=="GAME_NAME" set "GAME_NAME=%%b"
)

echo Copying files...
copy "../../scripts/" "%GAME_DIRECTORY%" /y

{COPY_FILES}
{ASSETS_RUN}
{ANGELSCRIPTPP_RUN}

set "J2L_LEVEL="
set "MUTATOR="

echo Starting
for %%i in (*.j2l) do (
  set "J2L_LEVEL=%%i"
  goto :check_mutator
)

:check_mutator
for %%i in (*.mut) do (
  set "MUTATOR=-mutators=%%i"
  goto :start_game
)

:start_game
if not defined J2L_LEVEL set "J2L_LEVEL=battle1"
"%GAME_DIRECTORY%%GAME_NAME%" -server %MUTATOR% %J2L_LEVEL%
@echo on

"""
example_script = """#pragma name "$N$"
#pragma require "STVutil.asc"

#include "STVutil.asc"

void onLevelBegin() {
	jjConsole("Started!");
}
"""
# data

from pick import pick
import os, shutil

mut_or_lvl = pick(["Mutator", "Level"], "Do you want to create a mutator or a level?", ">")
name = input("Name? ")
create_assets = pick(["No", "Yes"], "Assets? (y/n) ")
angelscriptPP = pick(["No", "Yes"], "AngelScript++? (y/n)")

directory = ("./mutators/" if mut_or_lvl[1] == 0 else "./levels/") + name

print(f"Creating new {'mutator' if mut_or_lvl[1] == 0 else 'level'} named {name}...")
os.makedirs(directory, exist_ok=True)

# if needs assets
if create_assets[1] == 1:
    os.makedirs(f"{directory}/assets/", exist_ok=True)
    run = run.replace(
        "{ASSETS_RUN}",
        assets_run.replace("$N$", f"STV{name}"), # without file extension
    )
else:
    run = run.replace("{ASSETS_RUN}", "")

# if using angelscript++
if angelscriptPP[1] == 1:
    run = run.replace("{ANGELSCRIPTPP_RUN}", angelscriptpp_run.replace("$N$", f"STV{name}"))  # without file extension
    run = run.replace("{COPY_FILES}", angelscriptpp_copy)
else:
    run = run.replace("{ANGELSCRIPTPP_RUN}", "")
    run = run.replace("{COPY_FILES}", normal_copy)

# write the run bat
with open(f"{directory}/run.bat", "w") as r:
    r.write(run)

# write the script file
with open(f"{directory}/STV{name}.{'mut' if mut_or_lvl[1] == 0 else 'j2as'}", "w") as f:
    if mut_or_lvl[1] == 0:
        # mutator
        f.write(example_script.replace("$N$", name))
    else:
        # level
        # remove the first line (which is the name for mutators)
        f.write("\n".join(example_script.split("\n")[1:]))

# if it's a level, copy an empty/example level
if not mut_or_lvl[1] == 0:
    shutil.copy("./empty.j2l", f"./levels/{name}/STV{name}.j2l")

print("Finished!")

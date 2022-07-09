# mcserverbot
Update: Very base function works<br/>
-Functions-<br/><br/><br/>
have a changeable operand or whatever its called like $command can change to .command<br/>
$copy -> copys a server<br/>
$send [server] [console command] -> sends some server commands<br/>
give more feedback for commands like $set <br/>
document all environment variables in something (maybe like $set help to get environment variable list and stuff)<br/>
make $help prettier<br/>
implement automatic cloudflare dns stuff<br/>
pipe most errors to an output 

Later: 
settings for modpack, vanilla, spigot, etc

forge api:

    MODS_FORGEAPI_KEY - Required
    MODS_FORGEAPI_FILE - Required or use MODS_FORGEAPI_PROJECTIDS (Overrides MODS_FORGEAPI_PROJECTIDS)
    MODS_FORGEAPI_PROJECTIDS - Required or use MODS_FORGEAPI_FILE
    MODS_FORGEAPI_RELEASES - Default is release, Options: [Release|Beta|Alpha]
    MODS_FORGEAPI_DOWNLOAD_DEPENDENCIES - Default is False, attempts to download required mods (releaseType Release) defined in Forge.
    MODS_FORGEAPI_IGNORE_GAMETYPE - Default is False, Allows for filtering mods on family type: FORGE, FABRIC, and BUKKIT. (Does not filter for Vanilla or custom)
    REMOVE_OLD_FORGEAPI_MODS - Default is False
    REMOVE_OLD_DATAPACKS_DEPTH - Default is 1
    REMOVE_OLD_DATAPACKS_INCLUDE - Default is *.jar


DONE:
$create -> goes through a process to create a new server, with all the options being steps that you can choose or something  
--creates a server in the list  
--sends commands to the docker (podman) to create a server based on that  
--maybe read the output till it says like "server up" and update the process to say like server successfully set up <br/><br/>
$stop -> stops the specified server <br/>
$start -> starts the specified server if it exists <br/>
$delete -> deletes the podman thing, probably should make it admin only or something  <br/>
$list -> list all servers, filtered based on server id <br/>

-- the command with the parameters -- <br/>

podman run -d -it \ <br/>
-e GUI=FALSE <br/>
-e EULA=TRUE \ <br/>
-e TYPE=$type '#FORGESPIGOTPAPERCURESFORGEetc' \  <br/>
-e VERSION=$version \  <br/>
-e FTB_MODPACK_ID=$ftbmodpackid '#only if ftb' \ <br/>
-e CF_SERVER_MOD=$modpackzip \ <br/>
-e WORLD=$worldzipurl \ <br/>
//server properties <br/>
-e OVERRIDE_SERVER_PROPERTIES=true  \ <br/>
-e '#all the options idk gl like DIFFICULTY=hard' \<br/>
-e SEED=$seed \ <br/>
-e LEVEL_TYPE=flat <br/>
//for autopause <br/>
-e MAX_TICK_TIME=-1 '#for autopause' \ <br/>
-e JVM_DD_OPTS=disable.watchdog:true \ <br/>
-e ENABLE_AUTOPAUSE=TRUE <br/>
//memory <br/>
-e MEMORY=$memory \ <br/>
-e INITMEMORY=$initialmemory \ <br/>
-e MAX_MEMORY=$maxmemory \ <br/>
-e EXEC_DIRECTLY=$exec '#if you want colors and stuff and also uses _docker attach_ instead of the other thing' \ <br/>


-p port:port \ <br/>
--name $name \ <br/>




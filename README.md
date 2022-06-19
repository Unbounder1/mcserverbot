# mcserverbot

- Functions -
have a changeable operand or whatever its called like $command can change to .command

$create -> goes through a process to create a new server, with all the options being steps that you can choose or something \n
--creates a server in the list \n 
--sends commands to the docker (podman) to create a server based on that
--maybe read the output till it says like "server up" and update the process to say like server successfully set up
$stop -> stops the specified server
$start -> starts the specified server if it exists
$delete -> deletes the podman thing, probably should make it admin only or something 
$list -> list all servers, filtered based on server id


Later:
$modpack http://example.com.zip -> so can install modpacks and/or datapacks automatically

-- the command with the parameters --


podman run -d -it \
-e GUI=FALSE
-e EULA=TRUE \
-e TYPE=$type '#FORGESPIGOTPAPERCURESFORGEetc' \ 
-e VERSION=$version \
-e FTB_MODPACK_ID=$ftbmodpackid '#only if ftb' \
-e CF_SERVER_MOD=$modpackzip \
-e WORLD=$worldzipurl \
//server properties
-e OVERRIDE_SERVER_PROPERTIES=true
-e '#all the options idk gl like DIFFICULTY=hard' \
-e SEED=$seed \
-e LEVEL_TYPE=flat
//for autopause
-e MAX_TICK_TIME=-1 '#for autopause' \
-e JVM_DD_OPTS=disable.watchdog:true \
-e ENABLE_AUTOPAUSE=TRUE
//memory
-e MEMORY=$memory \
-e INITMEMORY=$initialmemory \
-e MAX_MEMORY=$maxmemory \
-e EXEC_DIRECTLY=$exec '#if you want colors and stuff and also uses _docker attach_ instead of the other thing' \


-p port:port \
--name $name \

itzg/minecraft-server:$javaversion

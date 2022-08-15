# mcserverbot
Update: Very base function works<br/>
-Functions-<br/><br/><br/>
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




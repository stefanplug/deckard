<?php

$con=mysqli_connect("localhost","root","geefmefietsterug","nlnog");
// Check connection
if (mysqli_connect_errno())
{
    echo "Failed to connect to MySQL: " . mysqli_connect_error();
}

$staleout_time = 300;
if($_GET['staleout_time'])
{
    $staleout_time = $_GET['staleout_time'];
}

echo "<html><body><h2>Deckard ring</h2><p>Staleout time: <form action='" . $_PHP_SELF . "' method='GET'><input type='text' name='staleout_time'/><input type='submit' /></p>current staleout time is " . $staleout_time . " seconds</p>";

// create a list of which node have been seen by the server
$servers = mysqli_query($con,"SELECT id, hostname, v4 FROM machines WHERE deckardserver=1 AND v4 IS NOT NULL");
while($servers_row = mysqli_fetch_array($servers))
{
    echo "<table><th>IPv4</th></th><tr><td></td><td><b>Server:</b></td><td><b>" . $servers_row['hostname'] . "</b></td><td><b>" . $servers_row['v4'] . "</b></td></tr>";
    $nodes = mysqli_query($con,"SELECT id, hostname, v4 FROM machines WHERE (deckardserver = 0 OR deckardserver IS NULL) AND (v4 IS NOT NULL)");
    while($nodes_row = mysqli_fetch_array($nodes))
    {
        $server_seen = mysqli_query($con,"SELECT machinestates.tstamp, machinestates.active FROM machines, machinestates WHERE machines.id = machinestates.slave_id AND machinestates.slave_id=" . $nodes_row['id'] ." AND machinestates.master_id=" . $servers_row['id'] . " AND machinestates.protocol=4");
        $updatetime = mysqli_fetch_array($server_seen);
        $uptime = time() - $updatetime['tstamp'];  
        if($uptime > $staleout_time)
        {
            echo "<tr bgcolor=red><td><b>*</b></td><td><b>Node:</b></td><td><b>" . $nodes_row['hostname'] . "</b></td><td><b>" . $nodes_row['v4'] . "</b></td><td><b>has NOT been seen by the server</b></td></tr>";
        }
        else
        {
            echo "<tr><td></td><td><b>Node:</b></td><td><b>" . $nodes_row['hostname'] . "</b></td><td><b>" . $nodes_row['v4'] . "</b></td><td><b>last seen by server " . $uptime . " seconds ago</b></td></tr>";
        }
        $master_nodes = mysqli_query($con,"SELECT machines.hostname, machines.v4, machinestates.active, machinestates.tstamp FROM machines, machinestates WHERE machinestates.master_id=machines.id  AND machinestates.master_id!=" . $servers_row['id'] . " AND machinestates.slave_id=" . $nodes_row['id'] ." AND machinestates.protocol=4");
        while($masters = mysqli_fetch_array($master_nodes))
        {
            $updatetime = time() - $masters['tstamp'];
            if($updatetime < $staleout_time)
            {
                if($masters['active'] == 1)
                {
                    echo "<tr><td></td><td>was UP according to<td>" . $masters['hostname'] . "</td><td>" . $masters['v4'] . "</td><td>" . $updatetime . "</td><td>seconds ago</td></tr>";
                }
                else
                {
                    echo "<tr bgcolor='red'><td>*</td><td>was DOWN according to<td></td><td>" . $masters['hostname'] . "</td><td>" . $masters['v4'] . "</td><td>" . $updatetime . "</td><td>seconds ago</td></tr>";
                }
            }
        }
    }
}

// create a list of which node have been seen by the server
$servers6 = mysqli_query($con,"SELECT id, hostname, v6 FROM machines WHERE deckardserver=1 AND v6 IS NOT NULL");
while($servers_row6 = mysqli_fetch_array($servers6))
{
    echo "<table><th>IPv6</th><tr><td></td><td><b>Server:</b></td><td><b>" . $servers_row6['hostname'] . "</b></td><td><b>" . $servers_row6['v6'] . "</b></td></tr>";
    $nodes6 = mysqli_query($con,"SELECT id, hostname, v6 FROM machines WHERE (deckardserver = 0 OR deckardserver IS NULL) AND (v6 IS NOT NULL)");
    while($nodes_row6 = mysqli_fetch_array($nodes6))
    {
        $server_seen6 = mysqli_query($con,"SELECT machinestates.tstamp, machinestates.active FROM machines, machinestates WHERE machines.id = machinestates.slave_id AND machinestates.slave_id=" . $nodes_row6['id'] ." AND machinestates.master_id=" . $servers_row6['id'] . " AND machinestates.protocol=41");
        $updatetime6 = mysqli_fetch_array($server_seen6);
        $uptime6 = time() - $updatetime6['tstamp'];  
        if($uptime6 > $staleout_time)
        {
            echo "<tr bgcolor=red><td><b>*</b></td>";
        }
        else
        {
            echo "<tr><td></td>";
        }
        echo "</td><td><b>Node:</b></td><td><b>" . $nodes_row6['hostname'] . "</b></td><td><b>" . $nodes_row6['v6'] . "</b></td><td><b>last seen by server " . $uptime6 . " seconds ago</b></td></tr>";
        $master_nodes6 = mysqli_query($con,"SELECT machines.hostname, machines.v6, machinestates.active, machinestates.tstamp FROM machines, machinestates WHERE machinestates.master_id=machines.id AND machinestates.master_id!=" . $servers_row6['id'] . " AND machinestates.slave_id=" . $nodes_row6['id'] . " AND machinestates.protocol=41");
        while($masters6 = mysqli_fetch_array($master_nodes6))
        {
            $updatetime6 = time() - $masters6['tstamp'];
            if($updatetime6 < $staleout_time)
            {
                if($masters6['active'] == 1)
                {
                    echo "<tr><td></td><td></td><td>" . $masters6['hostname'] . "</td><td>" . $masters6['v6'] . "</td><td>UP " . $updatetime6 . " seconds ago</td></tr>";
                }
                else
                {
                    echo "<tr bgcolor='red'><td>*</td><td></td><td>" . $masters6['hostname'] . "</td><td>" . $masters6['v6'] . "</td><td>DOWN " . $updatetime6 . " seconds ago</td></tr>";
                }
            }
        }
    }
}
echo "</table></body></html>";

mysqli_close($con);
?>


<?php
$staleout_time = 55;

$con=mysqli_connect("localhost","root","geefmefietsterug","nlnog");
// Check connection
if (mysqli_connect_errno())
{
    echo "Failed to connect to MySQL: " . mysqli_connect_error();
}

echo "<html><body><h1>Deckard ring</h1><p>Staleout time: " . $staleout_time . " seconds</p><h2>IPv4</h>";
// create a list of which node have been seen by the server
$servers = mysqli_query($con,"SELECT id, hostname, v4 FROM machines WHERE deckardserver=1 AND v4 IS NOT NULL");
while($servers_row = mysqli_fetch_array($servers))
{
    echo "<table border=0><tr><td></td><td><b>Server:</b></td><td><b>" . $servers_row['hostname'] . "</b></td><td><b>" . $servers_row['v4'] . "</b></td></tr>";
    $nodes = mysqli_query($con,"SELECT id, hostname, v4 FROM machines WHERE (deckardserver = 0 OR deckardserver IS NULL) AND (v4 IS NOT NULL)");
    while($nodes_row = mysqli_fetch_array($nodes))
    {
        $server_seen = mysqli_query($con,"SELECT machinestates.tstamp, machinestates.active FROM machines, machinestates WHERE machines.id = machinestates.slave_id AND machinestates.slave_id=" . $nodes_row['id'] ." AND machinestates.master_id=" . $servers_row['id']);
        $updatetime = mysqli_fetch_array($server_seen);
        $uptime = time() - $updatetime['tstamp'];  
        if($uptime > $staleout_time)
        {
            echo "<tr bgcolor=red><td><b>*</b></td>";
        }
        else
        {
            echo "<tr><td></td>";
        }
        echo "</td><td><b>Node:</b></td><td><b>" . $nodes_row['hostname'] . "</b></td><td><b>" . $nodes_row['v4'] . "</b></td><td><b>last seen by server " . $uptime . " seconds ago</b></td></tr>";
        $master_nodes = mysqli_query($con,"SELECT machines.hostname, machines.v4, machinestates.active, machinestates.tstamp FROM machines, machinestates WHERE machinestates.master_id=machines.id  AND machinestates.master_id!=" . $servers_row['id'] . " AND machinestates.slave_id=" . $nodes_row['id'] ." AND machinestates.protocol=4");
        while($masters = mysqli_fetch_array($master_nodes))
        {
            $updatetime = time() - $masters['tstamp'];
            if($updatetime < $staleout_time)
            {
                if($masters['active'] == 1)
                {
                    echo "<tr><td></td><td></td><td>" . $masters['hostname'] . "</td><td>" . $masters['v4'] . "</td><td>UP " . $updatetime . " seconds ago</td></tr>";
                }
                else
                {
                    echo "<tr bgcolor='red'><td>*</td><td></td><td>" . $masters['hostname'] . "</td><td>" . $masters['v4'] . "</td><td>DOWN " . $updatetime . " seconds ago</td></tr>";
                }
            }
        }
    }
}

// create a list of which node have been seen by the server
echo "<br /><br /><h2>IPv6</h>";
$servers = mysqli_query($con,"SELECT id, hostname, v4 FROM machines WHERE deckardserver=1 AND v6 IS NOT NULL");
while($servers_row = mysqli_fetch_array($servers))
{
    echo "<table border=0><tr><td></td><td><b>Server:</b></td><td><b>" . $servers_row['hostname'] . "</b></td><td><b>" . $servers_row['v6'] . "</b></td></tr>";
    $nodes = mysqli_query($con,"SELECT id, hostname, v6 FROM machines WHERE (deckardserver = 0 OR deckardserver IS NULL) AND (v6 IS NOT NULL)");
    while($nodes_row = mysqli_fetch_array($nodes))
    {
        $server_seen = mysqli_query($con,"SELECT machinestates.tstamp, machinestates.active FROM machines, machinestates WHERE machines.id = machinestates.slave_id AND machinestates.slave_id=" . $nodes_row['id'] ." AND machinestates.master_id=" . $servers_row['id']);
        $updatetime = mysqli_fetch_array($server_seen);
        $uptime = time() - $updatetime['tstamp'];  
        if($uptime > $staleout_time)
        {
            echo "<tr bgcolor=red><td><b>*</b></td>";
        }
        else
        {
            echo "<tr><td></td>";
        }
        echo "</td><td><b>Node:</b></td><td><b>" . $nodes_row['hostname'] . "</b></td><td><b>" . $nodes_row['v6'] . "</b></td><td><b>last seen by server " . $uptime . " seconds ago</b></td></tr>";
        $master_nodes = mysqli_query($con,"SELECT machines.hostname, machines.v6, machinestates.active, machinestates.tstamp FROM machines, machinestates WHERE machinestates.master_id=machines.id  AND machinestates.master_id!=" . $servers_row['id'] . " AND machinestates.slave_id=" . $nodes_row['id']." AND machinestates.protocol=41");
        while($masters = mysqli_fetch_array($master_nodes))
        {
            $updatetime = time() - $masters['tstamp'];
            if($updatetime < $staleout_time)
            {
                if($masters['active'] == 1)
                {
                    echo "<tr><td></td><td></td><td>" . $masters['hostname'] . "</td><td>" . $masters['v6'] . "</td><td>UP " . $updatetime . " seconds ago</td></tr>";
                }
                else
                {
                    echo "<tr bgcolor='red'><td>*</td><td></td><td>" . $masters['hostname'] . "</td><td>" . $masters['v6'] . "</td><td>DOWN " . $updatetime . " seconds ago</td></tr>";
                }
            }
        }
    }
}
echo "</table></body></html>";

mysqli_close($con);
?>


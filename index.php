<?php
$staleout_time = 120;

$con=mysqli_connect("localhost","root","geefmefietsterug","nlnog");
// Check connection
if (mysqli_connect_errno())
{
    echo "Failed to connect to MySQL: " . mysqli_connect_error();
}

echo "<html><body><p>Deckard ring</p><p>Staleout time: " . $staleout_time . " seconds</p><p>IPv4</p>";


// create a list of which node have been seen by the server

echo "<p>The following table shows what nodes were seen by the server</p>";
$servers = mysqli_query($con,"SELECT id, hostname, v4 FROM machines WHERE deckardserver=1 AND v4 IS NOT NULL");
while($servers_row = mysqli_fetch_array($servers))
{
    echo "<table border=1><th>Table title</th><tr><td><span style='font-weight:bold'>Server:</span></td><td><span style='font-weight:bold'>" . $servers_row['hostname'] . "</span></td><td><span style='font-weight:bold'>" . $servers_row['v4'] . "</span></td></tr>";
    $nodes = mysqli_query($con,"SELECT id, hostname, v4 FROM machines WHERE (deckardserver = 0 OR deckardserver IS NULL) AND (v4 IS NOT NULL)");
    while($nodes_row = mysqli_fetch_array($nodes))
    {
        $server_seen = mysqli_query($con,"SELECT machinestates.tstamp,machinestate.active FROM machines, machinestates WHERE machines.id = machinestates.slave_id AND machinestates.slave_id=1"// . $nodes_row['id'] ." AND machinestates.master_id=" . $servers_row['id']);
        $updatetime = time() - $server_seen['machinestates.tstamp']; 
        echo "<tr><td>Node:</td><td>" . $nodes_row[hostname] . "</td><td>" . $nodes_row[v4] . "</td><td>last seen by server " . $updatetime . " seconds ago</td></tr>";
    }
}


/*

$nodes = mysqli_query($con,"SELECT machines.hostname, machines.v4, machinestates.active, machinestates.tstamp FROM machines, machinestates WHERE machinestates.master_id=machines.id AND machinestates.slave_id=());
"
// create the tables
$nodes = mysqli_query($con,"SELECT id, hostname, v4 FROM machines WHERE (deckardserver = 0 OR deckardserver IS NULL) AND (v4 IS NOT NULL)");
while($row = mysqli_fetch_array($nodes))
{
    echo "<table border='1'><tr><td><span style='font-weight:bold'>Slave node:</span></td><td><span style='font-weight:bold'>" . $row['hostname'] . "</span></td><td><span style='font-weight:bold'>" . $row['v4'] . "</span></td></tr>";
    $results = mysqli_query($con,"SELECT machines.hostname, machines.v4, machinestates.active, machinestates.tstamp FROM machines, machinestates WHERE machinestates.master_id=machines.id AND machinestates.slave_id=" . $row['id']);

    while($result = mysqli_fetch_array($results))
    {
        $updatetime = time() - $result['tstamp'];
        if($updatetime < $staleout_time)
        {
            echo "<tr><td>Master node:</td><td>" . $result['hostname'] . "</td><td>" . $result['v4'] . "</td>";
            if($result['active'] == 1)
            {
                echo "<td bgcolor='green'>up</td>";
            }
            else
            {
                echo "<td bgcolor='red'>down</td>";
            }
            echo "<td>" . $updatetime . " seconds ago</tr>";
        }
        echo "</table>";
    }
}
*/
echo "</table></body></html><body>";

mysqli_close($con);
?>


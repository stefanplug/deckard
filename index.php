<?php
$staleout_time = 120;

$con=mysqli_connect("localhost","root","geefmefietsterug","nlnog");
// Check connection
if (mysqli_connect_errno())
{
  echo "Failed to connect to MySQL: " . mysqli_connect_error();
}

echo "<html><body><p>Deckard ring</p><p>Staleout time: " . $staleout_time . " seconds</p><p>IPv4</p>";
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
        echo "<td>up</td>";
      }
      else
      {
        echo "<td>down</td>";
      }
      echo "<td>" . $updatetime . " seconds ago</tr>";
    }
    echo "</table>";
  }
}
echo "</table></body></html><body>";

mysqli_close($con);
?>


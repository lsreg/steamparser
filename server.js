var connect = require('connect');
var mysql= require('mysql');

var db=mysql.createConnection({
  host: '127.0.0.1',
  user: 'root',
  password:'11111',
  database:'steamparser'
});

function gameslist(req, res, next){
  res.setHeader('Content-Type','application/json');
  var query=
  "select gameid, gamename" +
  "  from games" +
  "  where gamename like ?;";
  db.query(
    query,
    ["%" + req.query['name'] + "%"],
    function(err,rows){
      if(err) throw err;
      res.end(JSON.stringify(rows));
    }
  );
}

function topgames(req, res, next){
  res.setHeader('Content-Type','application/json');
  var query=
  "select r2.gamesteamid, games.gamename, count(r2.id) as count " +
  "from usergames r1 " +
  "join usergames r2 on r1.usersteamid = r2.usersteamid " +
  "and r1.gamesteamid <> r2.gamesteamid " +
  "join games on r2.gamesteamid = games.gameid " +
  "where r1.gamesteamid = ? " +
  "group by r2.gamesteamid " +
  "order by count(r2.id) desc " +
  "limit 0,5;";
  db.query(
    query,
    [req.query['id']],
    function(err,rows){
      if(err) throw err;
      res.end(JSON.stringify(rows));
    }
  );
}


var app = connect();
app.use(connect.compress());
app.use(connect.static('public'));
app.use(connect.query());
app.use('/gameslist', gameslist);
app.use('/topgames', topgames);
app.use(function(req,res,next){
  res.setHeader('Content-Type','application/json');
  res.end(JSON.stringify(req.query));
});
app.listen(80);

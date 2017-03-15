var spawn = require('child_process').spawn;

var py = spawn('python', ['CrossDeptQuery.py'], {
    env:{ "PYTHONIOENCODING" : "cp65001" }
});

py.stdout.on('data', function (data) {
  console.log(data.toString());
});
//
//
// var spawn = require('child_process').spawn;
// var py = spawn('python',['CrossDeptQuery.py']);
// var data = [];
// var dataString = '';
// py.stdout.on('data', function(data){
// });
// py.stdin.write(JSON.stringify(data));
// py.stdin.end();

var PythonShell = require('python-shell');

var run = (pyfilepath) =>{
  PythonShell.run(pyfilepath, (err,results)=> {
    if (err) throw err;
    console.log(results);
    console.log('finished');
  });
}

// debug -------------------------
// -------------------------------
if(require.main === module){
  var PY_FILE_NAME = 'hello.py'
  run(PY_FILE_NAME);
} 

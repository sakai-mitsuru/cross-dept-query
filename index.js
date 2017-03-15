/**
 * cmd prompt using
 * chcp 65001
 * set PYTHONIOENCODING=utf-8
 */

var PythonShell = require('python-shell');
var PY_FILE_NAME = 'CrossDeptQuery.py';

// var run = (pyfilepath) =>{
//   PythonShell.run(pyfilepath, (err,results)=> {
//     if (err) throw err;
//     console.log(results);
//     console.log('finished');
//   });
// }

const pShellOn = (pyfilepath,msg) => {
  return new Promise((resolve,reject)=>{
    shellOn(resolve,reject,pyfilepath,msg)
  });
}

const shellOn = (resolve,reject,pyfilepath,msg) =>{
  var pyShell = new PythonShell(pyfilepath, {mode : 'json', args : [msg] });
  // var pyShell = new PythonShell(pyfilepath, {mode : 'json' });
  pyShell.on('message',(result)=>{
    console.log(result)
    resolve(result);
  });
  pyShell.end((err)=>{
    if(err) throw err;
  })
}

// debug -------------------------
// -------------------------------
if(require.main === module){
  // debug sample
  var sample = () =>{
    var file_path = 'CrossDeptQuery.py'
    run(file_path);
  }
  //sample();

  var main = () =>{
    var msg_ = 'Excelに詳しい人教えて';
    pShellOn(PY_FILE_NAME,msg_)
      .then((result)=>{
        console.log(result);
      })
      .catch((err)=>{
        console.dir(err);
      });
  }
  main();

}

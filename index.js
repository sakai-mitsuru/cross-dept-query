/**
 * cmd prompt using
 * chcp 65001
 * set PYTHONIOENCODING=utf-8
 */
var _ = require('lodash');
var PythonShell = require('python-shell');
var PY_FILE_NAME = 'CrossDeptQuery.py';

/**
 * promisified
 */
const pShellOn = (pyfilepath,msg) => {
  return new Promise((resolve,reject)=>{
    shellOn(resolve,reject,pyfilepath,msg)
  });
}

/**
 * execute py on pyhon shell
 * @param resolve {function} func on success
 * @param reject  {function} func on error
 * @param pyfilepath {string} python script file path
 * @param msg   {string}  original message for retrieve
 * @return {[string]} keywords [["1","keyword1"],["2","keyword2"],....]
 */
const shellOn = (resolve,reject,pyfilepath,msg) =>{
  // var pyShell = new PythonShell(pyfilepath, {mode : 'json' });
  var pyShell = new PythonShell(pyfilepath, {mode : 'json', args : [msg] });
  pyShell.on('message',(result)=>{
    let outAry = [];
    _.each(result,(ary)=>{
      // console.log(ary[1]);
      outAry.push(ary[1]);
    });
    //console.log(result)
    resolve(outAry);
  });
  pyShell.end((err)=>{
    if(err) throw err;
  })
}

// entry point
const main = (msg_) =>{
  let outAry = [];
  pShellOn(PY_FILE_NAME,msg_)
    .then((retAry)=>{
      console.log(retAry);
    })
    .catch((err)=>{
      console.dir(err);
    });
}

// export module
module.exports = pShellOn;

// debug -------------------------
// -------------------------------
if(require.main === module){
  // debug sample
  var sample = () =>{
    var file_path = 'CrossDeptQuery.py'
    run(file_path);
  }
  //sample();

  // debug execution
  const msg = 'Excelに詳しい人教えて';
  main(msg);
}

// # sample code
// var run = (pyfilepath) =>{
//   PythonShell.run(pyfilepath, (err,results)=> {
//     if (err) throw err;
//     console.log(results);
//     console.log('finished');
//   });
// }

/**
 * cmd prompt using
 *   not use powershell console
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
 * @return {[string]} keywords ["keyword1","keyword2",....]
 */
const shellOn = (resolve,reject,pyfilepath,msg) =>{
  var pyShell = new PythonShell(pyfilepath, {mode : 'text', args : [msg] });
  pyShell.on('message',(result)=>{
    //console.log(result)
    resolve(result);
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
    var file_path = PY_FILE_NAME
    run(file_path);
  }
  //sample();

  // debug execution
  // const msg = 'Excel';
  const msg = 'Excelに詳しい人教えて';
  main(msg);
}

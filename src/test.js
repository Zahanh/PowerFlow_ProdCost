const duckdb = require('duckdb');
const prompt = require('prompt-sync')();

var db = new duckdb.Database(':memory:');
const tableName = 'RESULTS'

// https://medium.com/@dcsenadheera777/run-python-script-using-nodejs-7b15abf2e531

db.all(select_all(tableName), function(err,res){
    if(err){
        throw err;
    }
    // This executes if there is no error [err]
    let tmp = prompt(`Choose a number 0 - ${Object.keys(res).length}`)
    
    print_db(res,Number(tmp))
    
});

/**
 * 
 * @param {string} tableName : name of a parquet database file
 * @returns SQL string to execute to open a parquet db.
 */
function select_all(tableName){
    assert(typeof(tableName) == 'string','Invalid table name input.')
    
    return `SELECT  * FROM READ_PARQUET('${tableName}.parquet')`
}

/**
 * 
 * @param {expression} condition : expression to check against (i.e. typeof(i) == 'string')
 * @param {string} message : message to print if assertion fails.
 */
function assert(condition, message){
    if (!condition){
        throw new Error(message || 'Assertion Failed.');
    }
}

function print_db(res, num){
    /**
     * This function prints out all of the objects inside the database.
     */
    if(typeof(num) === 'number'){
        if (num > Object.keys(res).length){
            num = Object.keys(res).length
        }
        for (let i = 0; i < num; i++){
            console.log(i)
            console.log(res[i])
        }
    }
    else{
        throw(TypeError)
    }
    
}

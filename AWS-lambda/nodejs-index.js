const https = require('https');

/**
 * Pass the data to send as `event.data`, and the request options as
 * `event.options`. For more information see the HTTPS module documentation
 * at https://nodejs.org/api/https.html.
 *
 * Will succeed with the response body.
 */
 
 var sanitize_re = /[^a-zA-Z0-9]/g ;
 
exports.handler = (event, context, callback) => {
    var apikey =  'apikey=' ;
    var dbowner = 'dbowner=JamesPerreault' ;
    var dbname = 'dbname=recipes.db' ;

    var sql = getCmd(event) ;
    
    //console.log(sql) ;
    //console.log(Buffer.from(sql).toString('base64')) ;
      
    var post =  [apikey,dbowner,dbname].join("&") ;
    post += "&sql=" + Buffer.from(sql).toString('base64') ;
    
    var options = {
        hostname: 'api.dbhub.io' ,
        port: 443,
        path: '/v1/query',
        method: 'POST',
        headers: {
        "Content-type": "application/x-www-form-urlencoded",
        'Content-Length': Buffer.byteLength(post)
        },
    };
    
      


   
    //console.log(options);
    const req = https.request(options, (res) => {
        let body = '';
        //console.log('Status:', res.statusCode);
        //console.log('Headers:', JSON.stringify(res.headers));
        res.setEncoding('utf8');
        res.on('data', (chunk) => body += chunk);
        res.on('end', () => {
            //console.log('Successfully processed HTTPS response');
            // If we know it's JSON, parse it
            if (res.headers['content-type'] === 'application/json') {
                body = JSON.parse(body);
            }
            var result = {
                isBase64Encoded : false,
                statusCode: res.statusCode,
                body:  body, //JSON.stringify(body),
                headers: {
                    "Content-Type": "text/plain", //"application/json" ,
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type,Apigw-Requestid", 
                    "Access-Control-Allow-Methods": "POST,GET,OPTIONS" 
                },
            } ;
            callback(null, result);
        });
    });
    req.on('error', callback);
    req.write(post);
    req.end();
};

function getCmd(event){
    var method ;
        if (event.queryStringParameters && event.queryStringParameters.method) {
          method = event.queryStringParameters.method ;
    }
    else {
        method =  "all" ;
    }
    if ( method == 'all') {
        return sqlAll() ;
    }
    else if (method == 'recipe') {
        return sqlRecipe(event.queryStringParameters) ;
    }
    else if (method == "ingredients") {
        return sqlIngredients(event.queryStringParameters) ;
    }
    else if (method == "search") {
        return sqlSearch(event.queryStringParameters) ;
    }
}

function sqlAll() {
    return  'select recipe.id, title, category, cuisine, rating, source,thumb\
            from recipe \
      left join categories on recipe.id == recipe_id WHERE deleted == FALSE ;';
}

function sqlRecipe(params) {
    var id ;
    if ( params.id) {
        id = params.id ;
        id = id.replace(sanitize_re,'') ;
    }
    else { id = 1 }
    return 'select recipe.id, title, category, cuisine, rating, source,link,description, \
       preptime,cooktime,servings,yields,yield_unit,modifications, instructions,image from recipe \
    left join categories on recipe.id = recipe_id WHERE recipe.id = ' +
    id + ';' ;
}
function sqlIngredients(params) {
    var id ;
    if ( params.id) {
        id = params.id ;
        id = id.replace(sanitize_re,'') ;
    }
    else { id = 1 }
    return 'select unit,amount,rangeamount,item,optional,inggroup,position \
     from ingredients WHERE deleted = FALSE AND recipe_id = ' + id + '\;' ;
}
function sqlSearch(params) {
    var q = params.q.replace(sanitize_re,'') ;
    return '   select DISTINCT recipe.id,title from recipe, ingredients \
        where title like \'%' + params.q + '%\' or item like \'%' + 
        q + '%\' and recipe.id = recipe_id ;' ; 
}



var dburl = '';
var dball = dburl ;
var dbrecipe = dburl + "?method=recipe&id=" ;
var dbing = dburl + "?method=ingredients&id=" ;
var dbsearch = dburl + "?method=search&q=" ;

function flatten_results(data) {
      var flat = data.map ( row => {
           var retval = {} ;
           row.forEach( col => {
              let value=col.Value ;
		   /*
	      if ( value == "<i>NULL</i>" ) {
		      value = "" ;
	      }
	      else  */
              if (col.Type == 4 || col.Type == 5 ) {
                 value=Number(value) ;
              }
              retval[col.Name] = value ;
           } ) ;
           return retval ;
       } ) ;
       return flat ;
}


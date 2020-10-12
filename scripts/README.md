Utility scripts for managing recipes. They all use a local copy of the database.  Any modifications made must be manually uploaded to [DBHub.io](https://DBHUB.io) in order to be used by the web application.

Here is a summary of each script:

* View recipes
    * print-recipes.py : print id and title of all recipes in database
    * gourmet-show-images.py : display images of specified recipes.
* Import recipes
    * gourmet-import-text-file.py : import a recipe from a text file.
    * gourmet-add-from-json.py : add a recipe created by the Gourmet [Chrome plugin](https://chrome.google.com/webstore/detail/gourmet-recipe-manager/bhneoidcckdhbjhmcpgbhhnapbbbojik).
    * gourmet-import-json.py : Import recipe from a recipe archive exported from [WebGourmet](https://www.gourmetrecipemanager.com)
* Modify recipes
    * gourmet-insert-image.py : Add an image to the specified recipe.  Creates the thumbnail version while adding.
    * gourmet-scale-images.py : Scales a recipe's image.

The remaining files are support modules. The files in the gourmet/ and default/ directory are from the original [Gourmet Recipe Manager](https://github.com/thinkle/gourmet/) and are used by the text file importer.

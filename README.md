# zeppelin-notebook-migration-tool

## installation / useage
```bash
git clone "https://github.com/market6/zeppelin-notebook-migration-tool" znmt
cd znmt
python z-migration.py -s <sourcedir> -t <targetdir> -c <confpath> -i <sourcenotebookid>
```
- *-s*: source directory of notebook(s) **required** *eg* `/opt/zeppelin_old/notebook`
- *-t*: target directory of notebook(s) **required** *eg* `/opt/zeppelin_new/notebook`
- *-i*: id of notebook **optional** *eg* `2B3SVVCBG`

#### Notes
- If `-i` is not specified, **all** notebooks will be coppied from the source to the target.
- The ID of the notebook can be found by going to the source directory and listing the directories. In each directory you will find a file called `note.json`. Open that file in your favorite editor and see if it more or less looks like the notebook you are looking for. 
-- Theoretically the ID listed in `note.json` can be different than the name of the directory. In this case, specify the name of the directory, and the tool will change the name in `note.json` at the target to match the name of the directory at the target. 
- If the ID already exists at the target, a new random ID will be generated. This can result in duplicate notebooks (say, if you use the tool twice). That is to say, this tool will not overwrite notebooks at the target (if it does you've found a bug). 
- If no `note.json` exists in the source, the tool will warn on an issue.  If you have 'issues' reported, check the logs. 
- The tool will generate a log file in the directory from which it was run.

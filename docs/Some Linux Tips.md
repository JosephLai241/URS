# Some Linux Tips

* You can further simplify running the program by making the program executable: 
  + `sudo chmod +x Urs.py` 
* Make sure the shebang at the top of `Urs.py` matches the location in which your Python3 is installed. You can use `which python` and then `python --version` to check. 
  + The default shebang is `#!/usr/bin/python`. 
* Now you will only have to prepend `./` to run URS. 
  + `./Urs.py ...` 
* Troubleshooting
  + You will have to set the fileformat to `UNIX` if you run URS with `./` and are greeted with a bad interpreter error. I did this using Vim. 

	``` 
    $ vim Urs.py
    :set fileformat=unix
    :wq!
    ```

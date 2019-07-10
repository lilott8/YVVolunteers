# YVVolunteers
A simple volunteer group generator.  This uses a greedy approach to build teams based on a user's skills and experience.

## Usage 
```
main.py 
    [-h] -i INPUT [-o OUTPUT] [-s SIZE] [-key KEY]
    [-g {magic,language,framework,naive,experience}] -t TAXONOMY
    [-pbt TEAMS]
```

### Required Flags:
 - `-i`/`--input`


## Description of Flags:

| Short             | Long              | Argument                                          | Purpose                               |
| ------------------|-------------------|---------------------------------------------------|---------------------------------------|
| -h                | -help             | -                                                 | Show this help message and exit.      |
| -i                | --input           | [path/to/input/file]                              | Provide input to the program.         |
| -o                | --output          | [path/to/output/]                                 | Provide the directory to write output.|
| -s                | --size            | integer                                           | Size of groups.                       |
| -key              | --key             | string                                            | What is the unique ID of the user?    |
| -g                | --group           | {magic, language, framework, naive, experience}   | How to build the groups.              |
| -t                | --taxonomy        | [path/to/taxonomy.json] file                      | Taxonomy for classifying skills.      |
| -pbt              | --teams           | [path/to/json/of/teams]                           | Path to prebuilt teams                |                                           


## Caveats

`-pbt` is not currently implemented.  Thus, to add new team members, this either must be run again or groups should be handled throug hand curation.

The organization of the output isn't too great.  For instance using `framework` or `language` it builds the teams accordingly, but gives not indication which group is proficient in which language or framework.

`magic` currently uses `naive`.  I want to implement a weighted group assigner; if I have more time, I will.
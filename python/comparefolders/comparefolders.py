import os
import sys
import fnmatch
import shutil

##### 

 # paths to compare
folders: list[str] = [

]

 # List of names to ignore
file_ignore = [
    
]

 # Operation Mode
 #    'compare'     will compare the files and make a list of all different files
 #     'fetch'      will compare the files, make a list and fetch the different files into a new folder.
 #      'dir'       will get the files from the paths and send them into the list with no comparing whatsoever.
op_mode = 'compare'

f_out = 'compare.log' # File to write the compared paths at

#####

f_files: list[list[str,]] = [] # All the files

f_list: list = [] # List with all file paths
c_list: list = [] # List with the paths of all different files

v_op_modes = ['compare','fetch','dir'] # All available operation modes
silent = False

dfile_count: int = 0

args = sys.argv
args.append("")

def send(msg:str) -> None:
    if silent: return
    print(msg)

def read_args(argv:list, op_mode:str, silent:bool, f_out:str) -> list[str]:
    tar = '' # Handling for special arguments
    op_mode = op_mode
    silent = silent
    f_out = f_out

    for i, arg in enumerate(argv):

        # Special argument handling
        if tar == '-i': # Add ignore
            file_ignore.append(arg)
        elif tar == '-o':
            f_out = arg or ''
        elif tar == '-m':
            if str.lower(arg) in v_op_modes: op_mode = arg
            else:
                op_mode = 'compare'
                print(f'Invalid operation mode: "{arg}"\nDefaulting to "compare" mode.')
        elif tar != '': raise Exception(f'Unknown arg: "{tar}"')

        if i == 0 or arg == '': continue # Ignore the first argument (it's always the file name)

        # Special argument check
        if arg[0] == '-' and tar == '':
            if arg == '-n': # Clear folders and file_ignore (useful if you're borrowing the script from somewhere)
                folders.clear()
                file_ignore.clear()
            elif arg == '-s': # Enable silent mode
                silent = True
            else:
                tar = arg
                continue
        elif tar == '': # Let's assume this is a folder path
            if not os.path.exists(arg) or os.path.isfile(arg): raise Exception(f'Not a folder path: "{arg}"')
            folders.append(arg)
        tar = ''
    
    return [op_mode, silent, f_out]

def create_file_directory(m_folder:str) -> None:
    '''
    Check a folder path and save all files' paths into f_files.
    Will also check and save subfolders.
    '''
    # Path error handling
    if not os.path.exists(m_folder):
        raise Exception(f'Path given does not exist: "{m_folder}"')

    dlist: list = []

    def bad_keyword(keyword:str, file:str) -> bool:
        if fnmatch.fnmatch(os.path.basename(file), keyword): return True
        return False

    def folder_routine(folder:str):
        for x in os.listdir(folder):
            # check our ignore keywords and ignore if the names match
            for k in file_ignore:
                if bad_keyword(k,x): return
            # Is this a file? if so, save the directory.
            cpath = os.path.join(folder, x)
            if os.path.isfile(cpath):
                dlist.append(f'\\{os.path.relpath(cpath, m_folder)}')
            # if not, let's go into *that* folder
            else: folder_routine(f'{cpath}\\')
    folder_routine(m_folder)

    f_files.append(dlist)
    
def compare(root:list, filelist:list) -> int:
    '''
    Compare files between different folders, using an already set file list.
    Saves different files and files that only exist in one directory.
    '''
    # Len diff handling

    def c_file(file:str) -> bool:
        return False
    
    files: list = []    # Files we're gonna compare
    binaries: list = [] # The files' binaries
    fpath: str = ''     # Our working path to check files
    atl = False         # (add-to-list) Is this file different?
    atlcount: int = 0   # How many files have been different so far?

    for dr in filelist:

        for x in root:
            # Simplify path and add to files to compare
            fpath = os.path.normpath(f'{x}{dr}')
            files.append(fpath)

            # Check if the files exist
            if not os.path.exists(fpath):
                # Directory doesn't exist in all main folders, discrepancy noted
                send(f'[X] {fpath}')
                atl = True
                break

        if not atl:

            for x in files:
                # We open file and add binaries to a list
                with open(x,'rb') as fr: # frfr
                    binaries.append([fr.readlines()])

            for i,x in enumerate(binaries):
                if i == 0: continue # Skip the first binaries as we can't compare them to an non-existent value
                if not binaries[i] == binaries[i-1]: # Compare to previous binaries, mark down if they're different
                    send(f'[!] {fpath}')
                    atl = True
                    break
                
            # If binaries don't match, note the discrepancy

        if atl:
            atlcount += 1
            c_list.append(dr.replace("\\", "/")) # Add to our list if it is a funny file
        files = []; atl = False; binaries = [] # Reset
    return atlcount

def clone_file(dir:str, to:str) -> None:
    to = f'{os.path.normpath(os.path.dirname(to))}\\'
    if not os.path.exists(to): os.makedirs(to)

    if os.path.exists(dir):
        shutil.copy(dir, to)
    else:
        if os.path.isfile(to): open(to, 'w')
        else: pass

# Argument handling
parg = read_args(args, op_mode, silent, f_out)
op_mode = parg[0]
silent = parg[1]
f_out = parg[2]

# Excecution Routine

if len(folders) == 0:
    print(f'Folder paths have not been provided. (Write them along with the script.)')
elif len(folders) == 1:
    print(f'You might want to provide at least 2 folders to compare.')
else:
    for fd in folders:
        create_file_directory(f'{fd}')
    for fl in f_files:
        f_list.extend(fl)
    f_list = sorted(list(set(f_list)))

    goal = c_list
    towrite = f'compare_result/' if op_mode == 'fetch' else '/'

    if op_mode == 'dir': goal = f_list
    else:
        dfile_count = compare(folders, f_list)

    if op_mode == 'fetch':
        for fd in folders:
            for fl in goal:
                clone_file(f'{fd}{fl}',f'{towrite}{fd}{fl}')

    if f_out != '':
        # Writing procedure
        if not os.path.exists(towrite): os.mkdir(towrite)
        with open(f'{towrite}{f_out}', 'w') as x:
            for l in goal:
                x.write(f'{l}\n')

b = os.getcwd().replace("\\", "/")

if not silent:
    if op_mode == 'compare':
        print(
            f'Finished. {len(f_list)} files were compared, {dfile_count} files were different.',
            f'\nPaths saved in "compare.log" @ "{b}/compare.log".' if f_out != '' else ''
            )
    elif op_mode == 'fetch':
        print(
            f'Finished. {len(f_list)} files were compared, {dfile_count} files were different.',
            f'\nPaths and files saved in "compare_result" folder @ "{b}/compare_result/".' if f_out != '' else ''
            )
    else: 
        print(
            f'Finished. {len(f_list)} paths have been saved.',
            f'\nPaths saved in "compare.log" @ "{b}/compare.log".' if f_out != '' else ''
            )
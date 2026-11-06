# filertk (version 0.9.0b)
<p>
filertk is a simple shell-based design focusing on general redundant file manipulation behaviors that typically take excessive work by hand.
</p>

# Commands
<p>
filertk's system works off of a select few commands for tokenization in no specific order. These tokens allow you to specify certain unique details on how you with for your program to operate.
</p>

<h2>Special Command Types:</h2>
<p>
Special Command Types are command types that will halt all instructions in order to complete a task.<br>
  <b>exit:</b> automatically closes filertk<br>
  <b>clear_res:</b> clears all files from filertk/results after display of files being deleted & confirmation, (closes program upon completion)<br>
</p>

<h2>Command Name & Range Identifiers</h2>
<p>
Name & Range identifiers allows filertk to interpret what matches and write instructions need to be made.<br>
  <b>"x" Name Operator:</b> Used for names just like strings, such as reader identifiers, writer identifiers, excluding identifiers, and ~s_copy identifiers (ex: match "text" with "new")<br>
  <b>(x-y) Range Operator:</b> Used for specifying the range for actions from start-finish inside of exclusions, and from statements (ex: from (1-10) excluding (5-5))<br><br>

  It's also very important to note each command must be spaced apart, even Name & Range identifiers!<br>
</p>

<h2>File Reader Types:</h2>
<p>
File Reader Types are command types that will specify how you want your matches to be made.<br>
  <b>match:</b> finds any words that contain the name identifier provided regardless of context<br>
  <b>exact:</b> finds words with an exact match to the name identifier provided<br><br>

  <h3>Read Identifier Types:</h3>
  <p>
  Read Identifier Types are special identifiers used for important exceptions amongst the match cases specified.<br>
    <b>excluding:</b> matches consisting of the name identifier provided or the range specified (inclusive) will be ignored<br>
    <b>from:</b> matches will only be considered within the start & ending range (inclusive)<br>
  </p>
</p>

<h2>File Writer Types:</h2>
<p>
File Writer Types are command types that will write the new text to the file based off the case specified.<br>
    <b>with:</b> Only replaces the matching text with the new writer name identifier (ex with "ex": "my_varExample" -> "exExample", "my_var20" -> "ex20")<br>
    <b>replace:</b> Fully replaces the matching text with the new writer name identifier (ex replace "ex": "my_varExample" -> "ex")<br>
    <b>r_append:</b> Appends the writer name identifier to the rear of the matches (ex r_append "ex": "my_varExample" -> "my_varExampleex")<br>
    <b>f_append:</b> Appends the writer name identifier to the front of the matches (ex f_append "ex": "my_varExample" -> "exmy_varExample")<br>
</p>

<h2>File Case Types</h2>
<p>
File Case Types are command types that describe how casings should be handled in a file.<br>
    <b>!case_ign:</b> Informs all casing cases are to be ignored, only the exact read name identifier and write name identifier provided are used <ins>(default case type)</ins><br>
    <b>!case_kp:</b> Attempts to keep all casing exact based off of character indexing (disclaimer: !case_kp is not recommended with mismatching reader and writer text sizes, unfavored results may occur)<br>
    <b>!r_case_ign:</b> All casing mismatches are ignored only for reading purposes<br>
</p>

<h2>File Copy Types</h2>
<p>
File Copy Types are command types that describe how the file modifications should be located.<br>
    <b>~h_copy:</b> Creates a hard copy of the original file; same exact name located inside of filertk's results/ directory <ins>(default copy type)</ins><br>
    <b>~modify:</b> Modifies the original file given, for safety purposes, a complete emergency backup copy is located in the results/ director titled "(filename)_backup"<br>
    <b>~s_copy:</b> Creates a shallow copy of the original file; a custom name (including extension) located in filertk's results/directory<br>
</p>

# Examples:
<p>
with "newtext" match "oldtext" from (10 - 20) excluding (5-5) !r_case_ign ~s_copy "newfile.txt"<br>
~h_copy exact "oldtext" replace "newtext"<br>
exact ~h_copy "oldtext" with "newtext"<br>
</p>

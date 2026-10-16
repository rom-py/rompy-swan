# Command index

Every SWAN command rompy-swan can write, and the component that writes it, by section of the command file. The index is generated from the code when the docs are built. The [SWAN user manual](https://swanmodel.sourceforge.io/online_doc/swanuse/swanuse.html) describes each command in full.

```python exec="on"
import sys

sys.path.insert(0, "scripts")
from command_index import command_index

print(command_index())
```

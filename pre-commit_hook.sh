#!/bin/bash

echo "#!/bin/sh" > .git/hooks/pre-commit
echo "black ." >> .git/hooks/pre-commit
echo "pylint HVAC_LOG680-01_H2023_EQ12" >> .git/hooks/pre-commit

chmod +x .git/hooks/pre-commit
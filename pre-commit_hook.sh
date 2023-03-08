#!/bin/bash

echo "#!/bin/sh" > .git/hooks/pre-commit
echo "black . --quiet" >> .git/hooks/pre-commit
echo "pylint --fail-under=9 HVAC_LOG680-01_H2023_EQ12" >> .git/hooks/pre-commit

chmod +x .git/hooks/pre-commit
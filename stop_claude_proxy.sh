#!/bin/bash
if [ -f litellm.pid ]; then
  kill $(cat litellm.pid)
  rm litellm.pid
  echo "Stopped LiteLLM"
fi

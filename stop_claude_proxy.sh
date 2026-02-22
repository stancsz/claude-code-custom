#!/bin/bash
if [ -f litellm.pid ]; then
  kill $(cat litellm.pid)
  rm litellm.pid
  echo "Stopped LiteLLM"
fi

if [ -f shim.pid ]; then
  kill $(cat shim.pid)
  rm shim.pid
  echo "Stopped Shim"
fi

#!/bin/bash
export ANTHROPIC_BASE_URL=http://localhost:4000
export ANTHROPIC_API_KEY=sk-ant-dummy
# OPENAI_API_KEY is already in env
claude "$@"

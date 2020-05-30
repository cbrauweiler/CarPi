#!/bin/bash

mount | grep media/. | cut -d' ' -f1,3

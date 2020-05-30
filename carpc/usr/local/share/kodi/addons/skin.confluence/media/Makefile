TARGET=Textures.xbt

IMAGES := $(shell find . -name "*jpg")
IMAGES += $(shell find . -name "*png")
IMAGES += $(shell find . -name "*gif")

all: $(TARGET)

.PHONY: force

$(TARGET): $(IMAGES)
ifeq (arm,arm)
	/home/pi/build/xbmc/tools/depends/native/TexturePacker/bin/TexturePacker -use_none -input . -output $(TARGET)
else
	/home/pi/build/xbmc/tools/depends/native/TexturePacker/bin/TexturePacker -input . -output $(TARGET)

endif

clean:
	rm -f $(TARGET)
distclean: clean


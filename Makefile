# Makefile für GTT Blotzman Code
# Einfaches Build-System als Alternative zu CMake

CC = gcc
CFLAGS = -O3 -Wall -Wextra -std=c11 -Iinclude
LDFLAGS = -lm

# Directories
SRC_DIR = src
INC_DIR = include
BUILD_DIR = build
LIB_DIR = lib

# Source files
SOURCES = $(SRC_DIR)/gtt_geometry.c \
          $(SRC_DIR)/fractal_rg.c \
          $(SRC_DIR)/gtt_background.c \
          $(SRC_DIR)/gtt_perturbations.c

OBJECTS = $(SOURCES:$(SRC_DIR)/%.c=$(BUILD_DIR)/%.o)

# Library
LIBRARY = $(LIB_DIR)/libgtt_blotzman.so

# Executables
TEST_BACKGROUND = $(BUILD_DIR)/test_background
TEST_PERTURBATIONS = $(BUILD_DIR)/test_perturbations

.PHONY: all clean test install

all: directories $(LIBRARY) $(TEST_BACKGROUND) $(TEST_PERTURBATIONS)

directories:
	@mkdir -p $(BUILD_DIR) $(LIB_DIR)

# Library
$(LIBRARY): $(OBJECTS)
	$(CC) -shared -o $@ $^ $(LDFLAGS)

# Object files
$(BUILD_DIR)/%.o: $(SRC_DIR)/%.c
	$(CC) $(CFLAGS) -fPIC -c $< -o $@

# Test executables
$(TEST_BACKGROUND): $(SRC_DIR)/gtt_background.c $(BUILD_DIR)/gtt_geometry.o $(BUILD_DIR)/fractal_rg.o
	$(CC) $(CFLAGS) -DGTT_BACKGROUND_MAIN $^ -o $@ $(LDFLAGS)

$(TEST_PERTURBATIONS): $(SRC_DIR)/gtt_perturbations.c $(BUILD_DIR)/gtt_geometry.o $(BUILD_DIR)/fractal_rg.o
	$(CC) $(CFLAGS) -DGTT_PERTURBATIONS_MAIN $^ -o $@ $(LDFLAGS)

# Run tests
test: $(TEST_BACKGROUND) $(TEST_PERTURBATIONS)
	@echo "=== Running Background Evolution Test ==="
	@$(TEST_BACKGROUND)
	@echo ""
	@echo "=== Running Perturbations Test ==="
	@$(TEST_PERTURBATIONS)

# Install
install: all
	@echo "Installing GTT Blotzman Code..."
	@mkdir -p /usr/local/lib
	@mkdir -p /usr/local/include/gtt_blotzman
	@cp $(LIBRARY) /usr/local/lib/
	@cp $(INC_DIR)/*.h /usr/local/include/gtt_blotzman/
	@ldconfig
	@echo "Installation complete!"

# Clean
clean:
	rm -rf $(BUILD_DIR) $(LIB_DIR)

# Help
help:
	@echo "GTT Blotzman Code - Build System"
	@echo ""
	@echo "Targets:"
	@echo "  all        - Build library and tests (default)"
	@echo "  test       - Run all tests"
	@echo "  install    - Install library and headers"
	@echo "  clean      - Remove build artifacts"
	@echo "  help       - Show this help message"

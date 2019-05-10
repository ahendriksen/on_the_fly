
# The number of epochs to train for
EPOCHS=1


# The targets which '.SECONDARY' depends on are treated as
# intermediate files, except that they are never automatically
# deleted.  *Note Chains of Implicit Rules: Chained Rules.

# '.SECONDARY' with no prerequisites causes all targets to be treated
# as secondary (i.e., no target is removed because it is considered
# intermediate).
.SECONDARY:


.PHONY:  training_set test_set
all: training_set test_set

REQUIRED_DIRS = data geometries processing reconstruction train test weights
_MKDIRS := $(shell for d in $(REQUIRED_DIRS); do [[ -d $$d ]] || mkdir -p $$d; done)

###############################################################################
#                                  Make data                                  #
###############################################################################

data/zoom1/.dirstamp: cone_balls_spec.txt
	mkdir -p $(@D)
	cone_balls foam --ball_spec $(<) --SOD 10.0 --SDD 10.0 --num_angles 1500 --Z 0.0 $(@D)
	touch $@

data/zoom4_centre/.dirstamp: cone_balls_spec.txt
	mkdir -p $(@D)
	cone_balls foam --ball_spec $(<) --SOD  2.5 --SDD 10.0 --num_angles 1500 --Z 0.0 $(@D)
	touch $@

data/zoom4_top/.dirstamp: cone_balls_spec.txt
	mkdir -p $(@D)
	cone_balls foam --ball_spec $(<) --SOD  2.5 --SDD 10.0 --num_angles 1500 --Z 0.3 $(@D)
	touch $@

###############################################################################
#                        Processing for reconstruction                        #
###############################################################################

processing/zoom4_centre_reprojection/.dirstamp: reconstruction/zoom1/.dirstamp
	otf-project with \
		input_dir=$(<D) \
		output_dir=$(@D) \
		projection_geometry=geometries/proj_geom_hr_centre.pickle \
		volume_geometry=geometries/vol_geom_lr.pickle \
		mask_volume_geometry=geometries/vol_geom_hr_centre.pickle \
		scan_type=simulation
	touch $@

processing/zoom4_top_reprojection/.dirstamp: reconstruction/zoom1/.dirstamp
	otf-project with \
		input_dir=$(<D) \
		output_dir=$(@D) \
		projection_geometry=geometries/proj_geom_hr_top.pickle \
		volume_geometry=geometries/vol_geom_lr.pickle \
		mask_volume_geometry=geometries/vol_geom_hr_top.pickle \
		scan_type=simulation
	touch $@


processing/%_processed/.dirstamp: data/%/.dirstamp processing/%_reprojection/.dirstamp
	otf-subtract with a=$(<D) b=$(word 2, $(^D)) output_dir=$(@D)
	touch $@

###############################################################################
#                                Reconstruction                               #
###############################################################################

reconstruction/zoom1/.dirstamp: data/zoom1/.dirstamp geometries/proj_geom_lr.pickle geometries/vol_geom_lr.pickle
	otf-reconstruct with \
		input_path=$(<D) \
		output_dir=$(@D) \
		projection_geometry=$(word 2, $^) \
		volume_geometry=$(word 3, $^) \
		scan_type=simulation
	touch $@

reconstruction/zoom4_centre/.dirstamp: processing/zoom4_centre_processed/.dirstamp geometries/proj_geom_hr_centre.pickle geometries/vol_geom_hr_centre.pickle
	otf-reconstruct with \
		input_path=$(<D) \
		output_dir=$(@D) \
		projection_geometry=$(word 2, $^) \
		volume_geometry=$(word 3, $^) \
		scan_type=simulation
	touch $@

reconstruction/zoom4_top/.dirstamp: processing/zoom4_top_processed/.dirstamp geometries/proj_geom_hr_top.pickle geometries/vol_geom_hr_top.pickle
	otf-reconstruct with \
		input_path=$(<D) \
		output_dir=$(@D) \
		projection_geometry=$(word 2, $^) \
		volume_geometry=$(word 3, $^) \
		scan_type=simulation
	touch $@

###############################################################################
#                                Train dataset                                #
###############################################################################

training_set: train/inputB/.dirstamp
training_set: train/inputA/.dirstamp
training_set: train/targetB/.dirstamp
training_set: train/targetA/.dirstamp

train/inputB/.dirstamp: reconstruction/zoom1/.dirstamp geometries/vol_geom_lr.pickle geometries/vol_geom_hr_centre.pickle
	otf-extract with \
		input_dir=$(<D) \
		output_dir=$(@D) \
		volume_geometry=$(word 2, $^) \
		mask_volume_geometry=$(word 3, $^)
	touch $@

train/inputA/.dirstamp: train/inputB/.dirstamp
	otf-resample with \
		input_dir=$(<D) \
		output_dir=$(@D) \
		factor=4 \
		direction='up' \
		method='nn'
	touch $@



train/targetA/.dirstamp: reconstruction/zoom4_centre/.dirstamp
	mkdir -p $(@D)
	ln $(<D)/*.tif $(@D)/
	touch $@

train/targetB/.dirstamp: reconstruction/zoom4_centre/.dirstamp
	otf-resample with \
		input_dir=$(<D) \
		output_dir=$(@D) \
		factor=4 \
		direction='down' \
		method='bicubic'
	touch $@

###############################################################################
#                                 Test dataset                                #
###############################################################################
test_set: test/inputB/.dirstamp
test_set: test/inputA/.dirstamp
test_set: test/targetB/.dirstamp
test_set: test/targetA/.dirstamp


test/inputB/.dirstamp: reconstruction/zoom1/.dirstamp geometries/vol_geom_lr.pickle geometries/vol_geom_hr_top.pickle
	otf-extract with \
		input_dir=$(<D) \
		output_dir=$(@D) \
		volume_geometry=$(word 2, $^) \
		mask_volume_geometry=$(word 3, $^)
	touch $@

test/inputA/.dirstamp: test/inputB/.dirstamp
	otf-resample with \
		input_dir=$(<D) \
		output_dir=$(@D) \
		factor=4 \
		direction='up' \
		method='nn'
	touch $@



test/targetA/.dirstamp: reconstruction/zoom4_top/.dirstamp
	mkdir -p $(@D)
	ln $(<D)/*.tif $(@D)/
	touch $@

test/targetB/.dirstamp: reconstruction/zoom4_top/.dirstamp
	otf-resample with \
		input_dir=$(<D) \
		output_dir=$(@D) \
		factor=4 \
		direction='down' \
		method='bicubic'
	touch $@

###############################################################################
#                                   Training                                  #
###############################################################################

train_all: weights/unet-B1.torch
train_all: weights/unet-A1.torch
train_all: weights/unet-A9.torch
train_all: weights/msd-B1.torch
train_all: weights/msd-A1.torch
train_all: weights/msd-A9.torch

weights/unet-B1.torch: train/inputB/.dirstamp train/targetB/.dirstamp
	otf-train with \
		input_dir=$(<D) \
		target_dir=$(word 2, $(^D)) \
		weights_file=$@ \
		slab_size=1 \
		epochs=$(EPOCHS) \
		network='unet'

weights/unet-A1.torch: train/inputA/.dirstamp train/targetA/.dirstamp
	otf-train with \
		input_dir=$(<D) \
		target_dir=$(word 2, $(^D)) \
		weights_file=$@ \
		slab_size=1 \
		epochs=$(EPOCHS) \
		network='unet'

weights/unet-A9.torch: train/inputA/.dirstamp train/targetA/.dirstamp
	otf-train with \
		input_dir=$(<D) \
		target_dir=$(word 2, $(^D)) \
		weights_file=$@ \
		slab_size=9 \
		epochs=$(EPOCHS) \
		network='unet'

weights/msd-B1.torch: train/inputB/.dirstamp train/targetB/.dirstamp
	otf-train with \
		input_dir=$(<D) \
		target_dir=$(word 2, $(^D)) \
		weights_file=$@ \
		slab_size=1 \
		epochs=$(EPOCHS) \
		network='msd'


weights/msd-A1.torch: train/inputA/.dirstamp train/targetA/.dirstamp
	otf-train with \
		input_dir=$(<D) \
		target_dir=$(word 2, $(^D)) \
		weights_file=$@ \
		slab_size=1 \
		epochs=$(EPOCHS) \
		network='msd'


weights/msd-A9.torch: train/inputA/.dirstamp train/targetA/.dirstamp
	otf-train with \
		input_dir=$(<D) \
		target_dir=$(word 2, $(^D)) \
		weights_file=$@ \
		slab_size=9 \
		epochs=$(EPOCHS) \
		network='msd'

###############################################################################
#                             Process test volume                             #
###############################################################################

all_outputs: test/output-unet-B/.dirstamp
all_outputs: test/output-unet-A1/.dirstamp
all_outputs: test/output-unet-A9/.dirstamp
all_outputs: test/output-msd-B/.dirstamp
all_outputs: test/output-msd-A1/.dirstamp
all_outputs: test/output-msd-A9/.dirstamp
all_outputs: test/output-bicubic/.dirstamp

test/output-bicubic/.dirstamp: test/inputB/.dirstamp
	otf-resample with \
		input_dir=$(<D) \
		output_dir=$(@D) \
		factor=4 \
		direction='up' \
		method='bicubic'
	touch $@

test/output-unet-B/.dirstamp: test/inputB/.dirstamp weights/unet-B1.torch
	otf-process with \
		input_dir=$(<D) \
		output_dir=$(@D) \
		weights_file=$(word 2, $^) \
		slab_size=1 \
		network='unet'
	touch $@

test/output-unet-A1/.dirstamp: test/inputA/.dirstamp weights/unet-A1.torch
	otf-process with \
		input_dir=$(<D) \
		output_dir=$(@D) \
		weights_file=$(word 2, $^) \
		slab_size=1 \
		network='unet'
	touch $@

test/output-unet-A9/.dirstamp: test/inputA/.dirstamp weights/unet-A9.torch
	otf-process with \
		input_dir=$(<D) \
		output_dir=$(@D) \
		weights_file=$(word 2, $^) \
		slab_size=9 \
		network='unet'
	touch $@

test/output-msd-B/.dirstamp: test/inputB/.dirstamp weights/msd-B1.torch
	otf-process with \
		input_dir=$(<D) \
		output_dir=$(@D) \
		weights_file=$(word 2, $^) \
		slab_size=1 \
		network='msd'
	touch $@


test/output-msd-A1/.dirstamp: test/inputA/.dirstamp weights/msd-A1.torch
	otf-process with \
		input_dir=$(<D) \
		output_dir=$(@D) \
		weights_file=$(word 2, $^) \
		slab_size=1 \
		network='msd'
	touch $@


test/output-msd-A9/.dirstamp: test/inputA/.dirstamp weights/msd-A9.torch
	otf-process with \
		input_dir=$(<D) \
		output_dir=$(@D) \
		weights_file=$(word 2, $^) \
		slab_size=9 \
		network='msd'
	touch $@

mkdir "mode_comparison(32+2gpus)"
cd "mode_comparison(32+2gpus)"
mkdir "two-step"
mkdir "default-g6k"
mkdir "bkz-only"
cd ..



for i in $(seq 1 5) #do
do
###########################################
# LWE instance solved by default G6K test
#
###########################################


python lwe_instance.py 59 --lwe/alpha 0.010 --threads 32 --gpus 2 --verbose True --pump/down_sieve True | tee "mode_comparison(32+2gpus)"/"default-g6k"/59-010-${i}.log


python lwe_instance.py 61 --lwe/alpha 0.010 --threads 32 --gpus 2 --verbose True --pump/down_sieve True | tee "mode_comparison(32+2gpus)"/"default-g6k"/61-010-${i}.log


# ###########################################
# # two-step mode
# #
# ###########################################


python lwe_instance_two_step.py 59 --lwe/alpha 0.010 --threads 32 --gpus 2 --verbose True --pump/down_sieve True  --bkz/blocksizes "[(10,1,1),(11,1,1),(12,1,1),(13,1,1),(14,1,1),(15,1,1),(16,1,1),(17,1,1),(18,1,1),(19,1,1),(20,1,1),(21,1,1),(22,1,1),(23,1,1),(24,1,1),(25,1,1),(26,1,1),(27,1,1),(28,1,1),(29,1,1),(30,1,1),(31,1,1),(32,1,1),(33,1,1),(34,1,1),(35,1,1),(36,1,1),(37,1,1),(38,1,1),(39,1,1),(40,1,1),(41,1,1),(42,1,1),(43,1,1),(44,1,1),(45,1,1),(46,1,1),(47,1,1),(48,1,1),(49,1,1),(69,1,1),(72,1,1),(75,1,1),(77,1,1),(79,1,1),(81,1,1),(83,1,1),(85,1,1),(87,1,1),(89,1,1),(91,1,1),(93,1,1),(95,1,1),(97,1,1)]" | tee "mode_comparison(32+2gpus)"/"two-step"/59-010-${i}.log

python lwe_instance_two_step.py 61 --lwe/alpha 0.010 --threads 32 --gpus 2 --verbose True --pump/down_sieve True  --bkz/blocksizes "[(10,1,1),(11,1,1),(12,1,1),(13,1,1),(14,1,1),(15,1,1),(16,1,1),(17,1,1),(18,1,1),(19,1,1),(20,1,1),(21,1,1),(22,1,1),(23,1,1),(24,1,1),(25,1,1),(26,1,1),(27,1,1),(28,1,1),(29,1,1),(30,1,1),(31,1,1),(32,1,1),(33,1,1),(34,1,1),(35,1,1),(36,1,1),(37,1,1),(38,1,1),(39,1,1),(40,1,1),(41,1,1),(42,1,1),(43,1,1),(44,1,1),(45,1,1),(46,1,1),(47,1,1),(48,1,1),(49,1,1),(71,1,1),(74,1,1),(77,1,1),(79,1,1),(81,1,1),(83,1,1),(85,1,1),(87,1,1),(89,1,1),(91,1,1),(93,1,1),(95,1,1),(97,1,1),(99,1,1),(101,1,1),(103,1,1),(105,1,1),(107,1,1)]"| tee "mode_comparison(32+2gpus)"/"two-step"/61-010-${i}.log

# ###########################################
# # bkz-only
# #
# ###########################################


python lwe_instance_BKZ_only.py 59 --lwe/alpha 0.010 --threads 32 --gpus 2 --verbose True --pump/down_sieve True | tee "mode_comparison(32+2gpus)"/"bkz-only"/59-010-${i}.log

python lwe_instance_BKZ_only.py 61 --lwe/alpha 0.010 --threads 32 --gpus 2 --verbose True --pump/down_sieve True | tee "mode_comparison(32+2gpus)"/"bkz-only"/61-010-${i}.log

done 
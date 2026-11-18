import vfs
from zephyr import FlashArea
block_dev = FlashArea(FlashArea.ID_storage, 4096)
vfs.VfsLfs2.mkfs(block_dev)

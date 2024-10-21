from shared.utils import get_guid


def test_uuid():
    # init
    storage_account_name = "mystorage"
    file_name = "myfile.mov"

    # act
    seed = f"{storage_account_name}-{file_name}"
    uuid_1 = get_guid(seed=seed)
    uuid_2 = get_guid(seed=seed)

    # validate
    assert uuid_1 == uuid_2

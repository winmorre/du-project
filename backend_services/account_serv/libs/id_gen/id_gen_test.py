from libs.id_gen import id_gen


def test_id_generated_successfully():
    new_id = id_gen.get_id()

    assert new_id
    assert new_id.bit_length() == 63  # unsigned integer (64 bit signed)


def test_multiple_id_generation():
    ids = {i: id_gen.get_id() for i in range(5)}

    assert ids[0] != ids[1]

    assert ids[2] > ids[0]

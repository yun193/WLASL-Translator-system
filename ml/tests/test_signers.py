from wlasl.signers import assign_folds, load_signers, resplit


def rec(vid, label, subset):
    return {"video_id": vid, "label": label, "subset": subset}


def test_assign_folds_balanced_and_complete():
    signer_of = {f"{i:05d}": i % 5 for i in range(50)}
    index = [rec(v, int(v) % 3, "train") for v in signer_of]
    index.append(rec("99999", 500, "train"))  # 只出現在詞彙表外類別的手語者
    signer_of["99999"] = 7
    folds = assign_folds(index, signer_of, 2, eval_classes=100)
    assert sorted(s for f in folds for s in f) == [0, 1, 2, 3, 4, 7]
    assert folds == assign_folds(index, signer_of, 2, eval_classes=100)  # 固定、可重現


def test_resplit_moves_holdout_to_test_and_keeps_seen_test():
    signer_of = {"a": 1, "b": 1, "c": 2, "d": 2}
    index = [rec("a", 0, "train"), rec("b", 0, "test"), rec("c", 0, "val"), rec("d", 0, "test")]
    out = {r["video_id"]: r["subset"] for r in resplit(index, signer_of, {1})}
    assert out == {"a": "test", "b": "test", "c": "val", "d": "test_seen"}
    assert index[0]["subset"] == "train"  # 原紀錄不動


def test_packaged_signer_map():
    m = load_signers()
    assert len(m) == 11980 and m["00335"] >= 0

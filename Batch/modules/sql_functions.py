import mph as _mph
import comsol as _comsol
import db_structure as _db_structure

def sweep_to_sql(
    model: _mph.Model,
    name,
    desc=None,
):
    _, light_sweep = model.outer('Data')
    i = 1
    params = {
        key: float(value)
        for key,
        value in _comsol.model_parameters(model).items()
        if 'light' not in key
    }
    params['name'] = name
    params['desc'] = desc

    notes = []
    for light_value in light_sweep:
        note = {}
        note.update(params)
        note['light'] = light_value
        df = _comsol.evaluate_expressions(model, i)
        note['data'] = df.to_json(index=True)
        notes.append(note)

        i += 1

    assert _db_structure.db.is_connection_usable(), 'Database not connected'
    _db_structure.Solve.insert_many(notes).execute()

import app


def create_pen(color, material):
    app.edit_db("insert into pens (color, material) values (?, ?);", (color, material))


def get_pens():
    return app.query_db("select * from pens;")


def create_part(title, pen_id):
    app.edit_db("insert into nodes (title, num_children, num_parents, pen_id) values (?, 0, 0, ?);", (title, pen_id))


def remove_part(id):
    app.edit_db("delete from nodes where id=?;", (id,))
    parent_edges = app.query_db("select from_node_id, to_node_id from edges where to_node_id=?", (id,))
    for edge in parent_edges:
        remove_edge(edge['from_node_id'], edge['to_node_id'])
    child_edges = app.query_db("select from_node_id, to_node_id from edges where from_node_id=?", (id,))
    for edge in child_edges:
        remove_edge(edge['from_node_id'], edge['to_node_id'])


def add_edge(from_node_id, to_node_id, pen_id):
    app.edit_db("insert into edges (from_node_id, to_node_id, pen_id) values (?, ?, ?);", (from_node_id, to_node_id, pen_id))
    app.edit_db("update nodes set num_parents = num_parents + 1 where id=?;", (to_node_id,))
    app.edit_db("update nodes set num_children = num_children + 1 where id=?;", (from_node_id,))


def remove_edge(from_node_id, to_node_id):
    app.edit_db("delete from edges where from_node_id=? and to_node_id=?", (from_node_id, to_node_id))
    app.edit_db("update nodes set num_parents = num_parents - 1 where id=?;", (to_node_id,))
    app.edit_db("update nodes set num_children = num_children - 1 where id=?;", (from_node_id,))


def get_part(id, all=False, pen_id=None):
    if all and pen_id is None:
        return app.query_db("select * from nodes;")
    elif all and pen_id:
        return app.query_db("select * from nodes where pen_id=?", (pen_id,))
    return app.query_db("select * from nodes where id=?;", (id,), True)


def get_assembly_subset(children, parents=None):
    # All assemblies
    if children and parents is None:
        return app.query_db("select * from nodes where num_children>0;")
    # All top-level assemblies
    elif children and not parents:
        return app.query_db("select * from nodes where num_children>0 and num_parents<1;")
    # All subassemblies
    elif children and parents:
        return app.query_db("select * from nodes where num_children>0 and num_parents>0;")
    # All component parts
    elif not children and parents:
        return app.query_db("select * from nodes where num_children<1 and num_parents>0;")
    # All orphan parts
    elif not children and not parents:
        return app.query_db("select * from nodes where num_children<1 and num_parents<1;")


def get_first_level_children(id):
    return app.query_db("select * from nodes left join edges on nodes.id=edges.to_node_id where edges.from_node_id=?;", (id,))


def get_all_assembly_parts(id):
    all_parts = [get_part(id)]
    children = get_first_level_children(id)
    for child_node in children:
        all_parts.extend(get_all_assembly_parts(child_node['id']))
    return all_parts


def get_parent_assemblies(id):
    parent_parts = []
    curr_id = id
    while True:
        parent = app.query_db("select * from nodes left join edges on nodes.id=edges.from_node_id where edges.to_node_id=?;", (curr_id,), True)
        if parent is None:
            break
        parent_parts.append(parent)
        curr_id = parent['id']
    return parent_parts

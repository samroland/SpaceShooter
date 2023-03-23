import params

class CollisionHandler():
    def __init__(self, session):
        self.session = session
        self.space = self.session.space
        self.entity_set = self.session.entity_set

        # bullet_handler = self.space.add_wildcard_collision_handler(params.cc_bullet)
        # bullet_handler.begin = self.remove_first_entity

        # Parameter order matters in the collision handlers
        # Typcially remove the first entity
        
        bullet_wall_handler = self.space.add_collision_handler(params.cc_bullet, params.cc_wall)
        bullet_wall_handler.begin = self.remove_first_entity

        bullet_enemy_handler = self.space.add_collision_handler(params.cc_bullet, params.cc_enemy)
        bullet_enemy_handler.begin = self.kill_enemy
        
        bullet_spawner_handler = self.space.add_collision_handler(params.cc_bullet, params.cc_spawner)
        bullet_spawner_handler.begin = self.hurt_spawner

        bullet_bh_handler = self.space.add_collision_handler(params.cc_bullet, params.cc_bh)
        bullet_bh_handler.begin = self.hurt_bh

        player_enemy_handler = self.space.add_collision_handler(params.cc_player, params.cc_enemy)
        player_enemy_handler.begin = self.kill_player

        player_bh_handler = self.space.add_collision_handler(params.cc_player, params.cc_bh)
        player_bh_handler.begin = self.kill_player

        enemy_bh_hadler = self.space.add_collision_handler(params.cc_enemy, params.cc_bh)
        enemy_bh_hadler.begin = self.absorb_enemy

        spawner_bh_hadler = self.space.add_collision_handler(params.cc_spawner, params.cc_bh)
        spawner_bh_hadler.begin = self.remove_first_entity

        bh_bh_handler = self.space.add_collision_handler(params.cc_bh, params.cc_bh)
        bh_bh_handler.begin = self.merge_bh

        return

    def get_entity(self, shape):
        return self.entity_set.shape_to_entity[shape]
    
    def remove_first_entity(self, arbiter, space, data):
        first_shape = arbiter.shapes[0]
        self.get_entity(first_shape).remove = True
        return False

    def kill_enemy(self, arbiter, space, data):
        self.remove_first_entity(arbiter, space, data)
        enemy_shape = arbiter.shapes[1]
        enemy = self.get_entity(enemy_shape)
        enemy.remove = True
        self.session.score += enemy.value
        return False

    def hurt_spawner(self, arbiter, space, data):
        self.remove_first_entity(arbiter, space, data)
        spawner_shape = arbiter.shapes[1]
        spawner = self.get_entity(spawner_shape)
        spawner.hurt()
        return False

    def kill_player(self, arbiter, space, data):
        self.session.kill_player()
        return False

    def merge_bh(self, arbiter, space, data):
        bh1, bh2 = [self.get_entity(s) for s in arbiter.shapes]
        bh1.remove = True
        bh2.value += bh1.value
        # bh2.g_mass += bh1.g_mass
        # bh2.shape.mass += bh1.shape.mass
        cm_v = (bh1.shape.mass*bh1.body.velocity + bh2.shape.mass*bh2.body.velocity)/(bh1.shape.mass+bh2.shape.mass)
        bh2.body.velocity = cm_v
        return False
    
    def absorb_enemy(self, arbiter, space, data):
        self.remove_first_entity(arbiter, space, data)
        enemy, bh = [self.get_entity(s) for s in arbiter.shapes]
        bh.value += params.bh_value_factor * enemy.value
        return False
    
    def hurt_bh(self, arbiter, space, data):
        self.remove_first_entity(arbiter, space, data)
        bh_shape = arbiter.shapes[1]
        bh = self.get_entity(bh_shape)
        bh.hurt()
        return False
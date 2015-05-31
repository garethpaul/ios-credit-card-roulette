//
//  ParticipantListItem.swift
//  CardRoulette
//
//  Created by Gareth Jones  on 5/31/15.
//  Copyright (c) 2015 gpj. All rights reserved.
//

import Foundation

class ParticipantListItem: NSObject{

    var itemName: NSString = ""
    var completed: Bool = false
    var creationDate: NSDate = NSDate()

    init(name:String){
        self.itemName = name
    }
    
}

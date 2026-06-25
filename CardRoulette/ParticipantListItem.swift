//
//  ParticipantListItem.swift
//  CardRoulette
//
//  Created by Gareth Jones  on 5/31/15.
//  Copyright (c) 2015 gpj. All rights reserved.
//

import Foundation

class ParticipantListItem: NSObject {

    var itemName = ""
    var completed: Bool = false
    var creationDate = Date()

    init(name: String) {
        self.itemName = name
        super.init()
    }

    class func normalizedName(_ name: String?) -> String? {
        if let participantName = name?.trimmingCharacters(in: .whitespacesAndNewlines),
           !participantName.isEmpty,
           participantName.unicodeScalars.contains(where: { scalar in
               let generalCategory = scalar.properties.generalCategory
               return generalCategory != .control && generalCategory != .format
           }) {
            return participantName
        }

        return nil
    }
    
}

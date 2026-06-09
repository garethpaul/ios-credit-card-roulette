//
//  CardRouletteTests.swift
//  CardRouletteTests
//
//  Created by Gareth Jones  on 5/30/15.
//  Copyright (c) 2015 gpj. All rights reserved.
//

import UIKit
import XCTest
@testable import CardRoulette

class CardRouletteTests: XCTestCase {

    func testParticipantNameNormalizationTrimsWhitespace() {
        XCTAssertEqual(ParticipantListItem.normalizedName("  Hemal\n")!, "Hemal", "Participant names should be trimmed before saving")
    }

    func testParticipantNameNormalizationRejectsBlankNames() {
        XCTAssertNil(ParticipantListItem.normalizedName("  \n\t  "), "Blank participant names should be ignored")
        XCTAssertNil(ParticipantListItem.normalizedName(nil), "Missing participant names should be ignored")
    }

}
